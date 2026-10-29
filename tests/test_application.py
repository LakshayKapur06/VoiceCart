"""System/automated story acceptance: real DB plus explicitly scripted extraction."""

import json
import os
import subprocess
import sys
import unittest

from tests.database_support import fabricated_document, isolated_database
from tests.test_nlu import extraction
from voicecart.application import ShoppingApplication
from voicecart.audio import Transcript, TranscriptKind
from voicecart.ingestion import parse_import
from voicecart.nlu import validate_interpretation


class ScriptedInterpreter:
    """No actual neural model. Validates scripted output through production checks."""

    def __init__(self):
        self.calls = 0

    def interpret(self, text, vocabulary):
        self.calls += 1
        if text == "add second":
            raw = extraction(
                intent="add",
                query=None,
                category=None,
                add_evidence="add",
                ordinal={"value": 2, "evidence": "second"},
            )
        elif text == "cheapest black backpack under 2000 and add":
            raw = extraction(
                intent="search_and_add",
                query="black backpack",
                objective="cheapest",
                add_evidence="add",
                colour={"value": "black", "evidence": "black"},
                price={"amount": "2000", "operator": "lt", "evidence": "under 2000"},
            )
        elif text == "backpack under 1":
            raw = extraction(
                price={"amount": "1", "operator": "lt", "evidence": "under 1"}
            )
        elif text == "drop constraints":
            raw = extraction(extra="execute")
        else:
            raw = extraction()
        return validate_interpretation(raw, text, vocabulary)


class ApplicationSystemTests(unittest.TestCase):
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
                "UPDATE catalogue_state SET revision='unpopulated',populated=false,coverage='unknown',valid_until=NULL,generation=NULL,dimensions=NULL,aliases='{}'"
            )
        self.database.publish(parse_import(fabricated_document()))
        self.interpreter = ScriptedInterpreter()
        self.app = ShoppingApplication(self.database, self.interpreter)
        self.session = self.app.sessions.create()

    def test_search_complete_list_select_add_and_repeat_without_mutation(self):
        result = self.app.text(self.session, "find backpack")
        self.assertEqual(result.code, "results")
        self.assertIn("rupees", result.text)
        self.assertTrue(
            self.app.sessions.mark_presented(
                self.session, result.listing.list_id, result.turn_id
            )
        )
        chosen = result.listing.offers[1]
        added = self.app.text(self.session, "add second")
        self.assertEqual(added.code, "added")
        self.assertEqual(added.receipt.variant_id, chosen.variant_id)
        calls = self.interpreter.calls
        self.assertEqual(self.app.text(self.session, "repeat"), added)
        self.assertEqual(self.interpreter.calls, calls)
        self.assertEqual(self.app.cart.items(self.session), {chosen.variant_id: 1})

    def test_duplicate_final_is_claimed_once_in_persistent_session(self):
        turn = self.app.begin(self.session)
        final = Transcript(
            TranscriptKind.FINAL, "cheapest black backpack under 2000 and add", turn
        )
        first = self.app.final(self.session, final)
        repeated = self.app.final(self.session, final)
        self.assertEqual(first.operation_id, repeated.operation_id)
        self.assertEqual(self.interpreter.calls, 1)
        self.assertEqual(self.app.cart.items(self.session), {"v-cheap": 1})

    def test_partial_blank_cancelled_and_malformed_requests_do_not_add(self):
        turn = self.app.begin(self.session)
        for kind, text in (
            (TranscriptKind.PARTIAL, "add"),
            (TranscriptKind.FINAL, " "),
        ):
            self.app.final(self.session, Transcript(kind, text, turn))
        self.app.cancel(self.session)
        stale = self.app.final(
            self.session, Transcript(TranscriptKind.FINAL, "add second", turn)
        )
        self.assertEqual(stale.code, "cancelled")
        result = self.app.text(self.session, "drop constraints")
        self.assertEqual(result.code, "clarify")
        self.assertEqual(self.app.cart.items(self.session), {})

    def test_unacknowledged_list_and_other_session_cannot_redirect_add(self):
        result = self.app.text(self.session, "find backpack")
        rejected = self.app.text(self.session, "add second")
        self.assertNotEqual(rejected.code, "added")
        other = self.app.sessions.create()
        self.assertFalse(
            self.app.sessions.mark_presented(
                other, result.listing.list_id, result.turn_id
            )
        )
        self.assertEqual(self.app.cart.items(self.session), {})

    def test_unpopulated_stale_and_no_match_are_different(self):
        none = self.app.text(self.session, "backpack under 1")
        self.assertEqual(none.code, "no_match")
        with self.database.connect() as connection:
            connection.execute("UPDATE catalogue_state SET valid_until='2000-01-01'")
        stale = self.app.text(self.session, "find backpack")
        self.assertEqual(stale.code, "catalogue_stale")
        with self.database.connect() as connection:
            connection.execute("TRUNCATE variant_search,variants,products CASCADE")
            connection.execute("UPDATE catalogue_state SET populated=false")
        empty = self.app.text(self.session, "find backpack")
        self.assertEqual(empty.code, "catalogue_not_populated")
        self.assertFalse(self.app.cart.items(self.session))

    def test_cancel_during_interpretation_fences_late_error_response(self):
        app = self.app

        class CancelledInterpreter:
            def interpret(inner, text, vocabulary):
                app.cancel(self.session)
                raise TimeoutError("Late inference callback")

        app.interpreter = CancelledInterpreter()
        response = app.text(self.session, "find backpack")
        self.assertEqual(response.code, "cancelled")
        self.assertEqual(response.text, "")
        self.assertEqual(app.cart.items(self.session), {})

    def test_template_error_after_commit_preserves_authoritative_confirmation(self):
        def broken(*args):
            raise ValueError("Injected rendering failure")

        self.app.confirmed_receipt = broken
        result = self.app.text(
            self.session, "cheapest black backpack under 2000 and add"
        )
        self.assertEqual(result.code, "added")
        self.assertIsNotNone(result.receipt)
        self.assertIn("committed", result.text)
        self.assertEqual(self.app.cart.items(self.session), {"v-cheap": 1})

    def test_real_cli_search_add_and_repeated_invocation_are_idempotent(self):
        import uuid

        environment = dict(
            os.environ, VOICECART_DATABASE_URL=os.environ["VOICECART_TEST_DSN"]
        )

        def invoke(*arguments):
            result = subprocess.run(
                [sys.executable, "-m", "voicecart", *arguments],
                env=environment,
                cwd="/tmp",
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)

        result = invoke("search", "--category", "backpack", "--colour", "black")
        session = result["session_id"]
        operation = str(uuid.uuid4())
        arguments = (
            "add",
            "--session-id",
            session,
            "--variant-id",
            "v-cheap",
            "--operation-id",
            operation,
        )
        first = invoke(*arguments)
        replay = invoke(*arguments)
        self.assertEqual(first, replay)
        self.assertEqual(self.app.cart.items(session), {"v-cheap": 1})
