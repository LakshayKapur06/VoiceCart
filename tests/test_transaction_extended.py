"""Guarded real SQL concurrency and controlled commit/clock failure windows."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import psycopg

from tests import test_cart as cart_tests
from tests.database_support import fabricated_document
from voicecart.cart import CartError, OutcomeUnknown
from voicecart.cart_management import CartManagement
from voicecart.database import DatabaseUnavailable
from voicecart.ingestion import parse_import
from voicecart.sessions import SessionError


class ExtendedTransactionTests(unittest.TestCase):
    setUpClass = classmethod(cart_tests.CartIntegrationTests.setUpClass.__func__)
    setUp = cart_tests.CartIntegrationTests.setUp
    command = cart_tests.CartIntegrationTests.command

    def seed_line(self):
        self.cart.add(self.command())
        return CartManagement(self.database)

    def test_parallel_target_updates_duplicate_payload_and_immutable_replay(self):
        management = self.seed_line()
        operations = [str(uuid.uuid4()), str(uuid.uuid4())]
        with ThreadPoolExecutor(max_workers=2) as workers:
            results = list(
                workers.map(
                    lambda pair: CartManagement(self.database).set_quantity(
                        self.session, pair[0], "v-cheap", pair[1], "INR"
                    ),
                    zip(operations, [2, 3], strict=True),
                )
            )
        final = management.overview(self.session)["items"][0]["quantity"]
        self.assertIn(final, (2, 3))
        for receipt, quantity in zip(results, [2, 3], strict=True):
            self.assertEqual(receipt["quantity"], quantity)
            self.assertEqual(
                management.set_quantity(
                    self.session, receipt["operation_id"], "v-cheap", quantity, "INR"
                ),
                receipt,
            )
        self.assertEqual(
            management.overview(self.session)["items"][0]["quantity"], final
        )
        with self.assertRaises(CartError):
            management.set_quantity(self.session, operations[0], "v-cheap", 1, "INR")

    def test_failure_before_commit_rolls_back_and_original_id_recovers(self):
        management = self.seed_line()
        operation = str(uuid.uuid4())
        connect = self.database.connect
        calls = 0

        @contextmanager
        def interrupted():
            nonlocal calls
            calls += 1
            with connect() as connection:
                yield connection
                if calls == 1:
                    raise psycopg.OperationalError("TEST precommit connection failure")

        with (
            patch.object(self.database, "connect", interrupted),
            self.assertRaises(OutcomeUnknown),
        ):
            management.set_quantity(self.session, operation, "v-cheap", 2, "INR")
        self.assertEqual(management.overview(self.session)["items"][0]["quantity"], 1)
        self.assertIsNone(management.receipt(self.session, operation))
        management.set_quantity(self.session, operation, "v-cheap", 2, "INR")
        self.assertEqual(management.overview(self.session)["items"][0]["quantity"], 2)

    def test_loss_after_commit_reconciles_authoritative_adjustment(self):
        management = self.seed_line()
        operation = str(uuid.uuid4())
        connect = self.database.connect
        calls = 0

        @contextmanager
        def lost_reply():
            nonlocal calls
            calls += 1
            with connect() as connection:
                yield connection
            if calls == 1:
                raise psycopg.OperationalError("TEST commit succeeded, reply lost")

        with patch.object(self.database, "connect", lost_reply):
            receipt = management.set_quantity(
                self.session, operation, "v-cheap", 2, "INR"
            )
        self.assertEqual(receipt["status"], "committed")
        self.assertEqual(management.overview(self.session)["items"][0]["quantity"], 2)

    def test_postcommit_receipt_outage_is_unknown_then_same_id_replays(self):
        management = self.seed_line()
        operation = str(uuid.uuid4())
        with (
            patch.object(
                management,
                "receipt",
                side_effect=DatabaseUnavailable("TEST verify outage"),
            ),
            self.assertRaises(OutcomeUnknown),
        ):
            management.set_quantity(self.session, operation, "v-cheap", 2, "INR")
        recovered = CartManagement(self.database).receipt(self.session, operation)
        self.assertEqual(recovered["status"], "committed")
        self.assertEqual(
            management.set_quantity(self.session, operation, "v-cheap", 2, "INR"),
            recovered,
        )
        self.assertEqual(management.overview(self.session)["items"][0]["quantity"], 2)

    def test_session_expiry_during_snapshot_blocks_add_before_write(self):
        snapshot = self.database.snapshot_in
        now = datetime.now(UTC)
        with patch("voicecart.sessions.datetime") as clock:
            clock.now.return_value = now

            def delayed(connection):
                result = snapshot(connection)
                clock.now.return_value = now + timedelta(hours=2)
                return result

            with (
                patch.object(self.database, "snapshot_in", delayed),
                self.assertRaises(CartError) as expired,
            ):
                self.cart.add(self.command())
            self.assertEqual(expired.exception.code, "invalid_or_expired_operation")
        self.assertEqual(self.cart.items(self.session), {})

    def test_session_expiry_during_quantity_eligibility_blocks_write(self):
        management = self.seed_line()
        snapshot = self.database.snapshot_in
        now = datetime.now(UTC)
        operation = str(uuid.uuid4())
        with patch("voicecart.sessions.datetime") as clock:
            clock.now.return_value = now

            def delayed(connection):
                result = snapshot(connection)
                clock.now.return_value = now + timedelta(hours=2)
                return result

            with (
                patch.object(self.database, "snapshot_in", delayed),
                self.assertRaises(SessionError),
            ):
                management.set_quantity(self.session, operation, "v-cheap", 2, "INR")
        self.assertEqual(management.overview(self.session)["items"][0]["quantity"], 1)
        self.assertIsNone(management.receipt(self.session, operation))

    def test_product_deactivation_after_search_prevents_add(self):
        command = self.command()
        raw = fabricated_document("fixture-deactivated", "fixture-1")
        # Find the exact selected parent instead of relying on an unrelated product.
        parent = next(
            v["product_id"] for v in raw["variants"] if v["variant_id"] == "v-cheap"
        )
        for product in raw["products"]:
            if product["product_id"] == parent:
                product["active"] = False
        self.database.publish(parse_import(raw))
        with self.assertRaises(CartError):
            self.cart.add(command)
        self.assertEqual(self.cart.items(self.session), {})
