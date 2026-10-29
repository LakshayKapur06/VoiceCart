"""Real PostgreSQL transactions with isolated fabricated catalogue records."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import psycopg

from tests.database_support import fabricated_document, isolated_database
from voicecart.cart import AddCommand, CartError, CartService, OutcomeUnknown
from voicecart.database import DatabaseUnavailable
from voicecart.domain import HardConstraints, SearchRequest
from voicecart.ingestion import parse_import
from voicecart.search import PostgresCatalogue
from voicecart.sessions import SessionError, SessionStore


class CartIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute(
                "TRUNCATE sessions,commands,result_lists,cart_items,operation_receipts CASCADE"
            )
            connection.execute("TRUNCATE variant_search,variants,products CASCADE")
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',coverage='unknown',populated=false,valid_until=NULL,generation=NULL,dimensions=NULL,aliases='{}'"
            )
        self.database.publish(parse_import(fabricated_document()))
        self.sessions = SessionStore(self.database)
        self.cart = CartService(self.database)
        self.session = self.sessions.create()
        self.turn = self.sessions.begin_turn(self.session)

    def command(
        self,
        *,
        variant="v-cheap",
        quantity=1,
        selection="exact",
        session=None,
        turn=None,
    ):
        return AddCommand(
            session or self.session,
            turn or self.turn,
            str(uuid.uuid4()),
            selection,
            SearchRequest(
                HardConstraints(
                    "INR", category="backpack", colour="black", quantity=quantity
                )
            ),
            variant if selection == "exact" else None,
        )

    def test_commit_verified_by_immutable_receipt_and_retry_exactly_once(self):
        command = self.command()
        receipt = self.cart.add(command)
        self.assertEqual(receipt.added_quantity, 1)
        self.assertEqual(receipt.line_price_minor, 50000)
        self.assertEqual(self.cart.add(command), receipt)
        self.assertEqual(
            CartService(self.database).retry(self.session, command.operation_id),
            receipt,
        )
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})
        with self.database.connect() as connection:
            with self.assertRaises(psycopg.Error):
                connection.execute(
                    "UPDATE operation_receipts SET resulting_quantity=99 WHERE operation_id=%s",
                    (command.operation_id,),
                )

    def test_parallel_duplicate_workers_apply_one_increment(self):
        command = self.command()

        def add(_):
            return CartService(self.database).add(command).operation_id

        with ThreadPoolExecutor(max_workers=6) as workers:
            receipts = list(workers.map(add, range(12)))
        self.assertEqual(set(receipts), {command.operation_id})
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_new_intentional_add_and_old_receipt_remain_distinct(self):
        original = self.command()
        first = self.cart.add(original)
        self.cart.add(self.command())
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 2})
        replay = self.cart.add(original)
        self.assertEqual(replay.resulting_quantity, first.resulting_quantity)
        self.assertEqual(replay.resulting_quantity, 1)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 2})

    def test_same_operation_different_payload_or_session_is_conflict(self):
        command = self.command()
        self.cart.add(command)
        with self.assertRaises(CartError):
            self.cart.add(
                replace(
                    command, request=SearchRequest(HardConstraints("INR", quantity=2))
                )
            )
        other = self.sessions.create()
        turn = self.sessions.begin_turn(other)
        with self.assertRaises(CartError):
            self.cart.add(replace(command, session_id=other, turn_id=turn))
        self.assertEqual(self.cart.items(other), {})

    def test_aggregate_stock_blocks_fourth_add(self):
        self.cart.add(self.command(quantity=3))
        with self.assertRaises(CartError):
            self.cart.add(self.command())
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 3})
        self.assertIsNone(self.cart.pending(self.session))

    def test_cheapest_replay_is_before_new_query_selection(self):
        command = self.command(selection="cheapest")
        first = self.cart.add(command)
        raw = fabricated_document("fixture-2", "fixture-1")
        raw["variants"][0]["price"]["minor_units"] = 1
        self.database.publish(parse_import(raw))
        replay = self.cart.add(command)
        self.assertEqual(replay.variant_id, first.variant_id)
        self.assertEqual(replay.unit_price_minor, first.unit_price_minor)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})
        self.assertEqual(
            self.cart.add(self.command(selection="cheapest")).variant_id, "v-best"
        )

    def test_cheapest_accounts_for_existing_cart_quantity(self):
        self.cart.add(self.command(quantity=3))
        receipt = self.cart.add(self.command(selection="cheapest"))
        self.assertEqual(receipt.variant_id, "v-best")

    def test_changed_offer_and_partial_coverage_never_commit(self):
        command = replace(self.command(), expected_revision="old-revision")
        with self.assertRaises(CartError):
            self.cart.add(command)
        with self.database.connect() as connection:
            connection.execute("UPDATE catalogue_state SET coverage='partial'")
        with self.assertRaises(CartError):
            self.cart.add(self.command(selection="cheapest"))
        self.assertEqual(self.cart.items(self.session), {})

    def test_late_turn_cancel_and_precommit_cancellation_do_not_add(self):
        stale = self.command()
        self.sessions.begin_turn(self.session)
        with self.assertRaises(CartError):
            self.cart.add(stale)
        self.turn = self.sessions.begin_turn(self.session)
        command = self.command()
        self.cart.prepare(command)
        self.sessions.cancel(self.session)
        with self.assertRaises(CartError):
            self.cart.add(command)
        self.turn = self.sessions.begin_turn(self.session)
        event = threading.Event()
        event.set()
        with self.assertRaises(CartError):
            self.cart.add(self.command(), cancelled=event)
        self.assertEqual(self.cart.items(self.session), {})

    def test_stop_after_commit_does_not_undo_receipt(self):
        command = self.command()
        receipt = self.cart.add(command)
        self.sessions.cancel(self.session)
        self.assertEqual(
            self.cart.read_receipt(self.session, command.operation_id), receipt
        )
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_commit_reply_loss_reconciles_original_receipt(self):
        class LostReply(CartService):
            def _execute_once(inner, command, cancelled):
                super()._execute_once(command, cancelled)
                raise DatabaseUnavailable("Injected loss after successful commit")

        command = self.command()
        receipt = LostReply(self.database).add(command)
        self.assertEqual(receipt.operation_id, command.operation_id)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_unknown_outcome_keeps_identity_and_can_be_recovered_after_restart(self):
        class Uncertain(CartService):
            def _execute_once(inner, command, cancelled):
                super()._execute_once(command, cancelled)
                raise DatabaseUnavailable("Injected lost commit acknowledgement")

            def read_receipt(inner, *args):
                raise DatabaseUnavailable("Injected reconciliation outage")

        command = self.command()
        with self.assertRaises(OutcomeUnknown):
            Uncertain(self.database).add(command)
        receipt = CartService(self.database).retry(self.session, command.operation_id)
        self.assertEqual(receipt.operation_id, command.operation_id)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_pending_precommit_outage_blocks_replacement_operation(self):
        class BeforeCommitOutage(CartService):
            def _execute_once(inner, command, cancelled):
                raise DatabaseUnavailable("Injected unavailable DB before mutation")

        command = self.command()
        with self.assertRaises(OutcomeUnknown):
            BeforeCommitOutage(self.database).add(command)
        self.assertEqual(self.cart.pending(self.session), command.operation_id)
        with self.assertRaises(CartError):
            self.cart.add(self.command())
        self.cart.retry(self.session, command.operation_id)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_whole_transaction_retry_uses_original_operation(self):
        class Transient(CartService):
            calls = 0

            def _execute_once(inner, command, cancelled):
                inner.calls += 1
                if inner.calls == 1:
                    raise psycopg.errors.SerializationFailure(
                        "Injected retryable fault"
                    )
                return super()._execute_once(command, cancelled)

        service = Transient(self.database)
        service.add(self.command())
        self.assertEqual(service.calls, 2)
        self.assertEqual(self.cart.items(self.session), {"v-cheap": 1})

    def test_session_isolation_and_expiry_cleanup(self):
        command = self.command()
        self.cart.add(command)
        other = self.sessions.create()
        self.assertEqual(self.cart.items(other), {})
        self.assertIsNone(self.cart.read_receipt(other, command.operation_id))
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE sessions SET expires_at='2000-01-01' WHERE session_id=%s",
                (self.session,),
            )
        with self.assertRaises(SessionError):
            self.cart.items(self.session)
        self.assertEqual(self.sessions.cleanup_expired(), 1)
        with self.database.connect() as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) AS n FROM commands WHERE session_id=%s",
                    (self.session,),
                ).fetchone()["n"],
                0,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) AS n FROM operation_receipts WHERE session_id=%s",
                    (self.session,),
                ).fetchone()["n"],
                0,
            )
        self.assertEqual(self.database.inspect()["product_count"], 3)

    def test_result_ordinals_require_current_complete_presentation(self):
        result = PostgresCatalogue(self.database).search(
            SearchRequest(HardConstraints("INR", category="backpack"))
        )
        listing = self.sessions.publish_results(self.session, self.turn, result)
        with self.assertRaises(SessionError):
            self.sessions.resolve(self.session, 1)
        self.assertTrue(
            self.sessions.mark_presented(self.session, listing.list_id, self.turn)
        )
        first = self.sessions.resolve(self.session, 1)
        self.assertEqual(first.variant_id, listing.offers[0].variant_id)
        new_turn = self.sessions.begin_turn(self.session)
        self.assertFalse(
            self.sessions.mark_presented(self.session, listing.list_id, self.turn)
        )
        replacement = self.sessions.publish_results(self.session, new_turn, result)
        with self.assertRaises(SessionError):
            self.sessions.resolve(self.session, 1, list_id=listing.list_id)
        self.assertNotEqual(replacement.list_id, listing.list_id)
