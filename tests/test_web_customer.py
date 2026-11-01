"""Real HTTP/customer/cart system tests; synthetic offers only in guarded SQL."""

import hashlib
import http.client
import json
import os
import threading
import unittest
import uuid

from tests.database_support import fabricated_document, isolated_database
from voicecart.cart_management import CartManagement
from voicecart.ingestion import parse_import
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings


class CustomerHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute(
                "TRUNCATE sessions,variant_search,variants,products CASCADE"
            )
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',populated=false"
            )
        self.database.publish(parse_import(fabricated_document()))
        app = WebApplication(
            {
                "local": Merchant(
                    Settings(os.environ["VOICECART_TEST_DSN"]),
                    hashlib.sha256(b"TEST-ONLY-KEY").hexdigest(),
                )
            },
            b"x" * 32,
        )
        self.server = Server(("127.0.0.1", 0), app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        self.cookie = ""

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)

    def request(self, resource, body=None):
        self.client.request(
            "POST" if body is not None else "GET",
            "/api/local/" + resource,
            body=json.dumps(body) if body is not None else None,
            headers={"Content-Type": "application/json", "Cookie": self.cookie},
        )
        reply = self.client.getresponse()
        status = reply.status
        if reply.getheader("Set-Cookie"):
            self.cookie = reply.getheader("Set-Cookie").split(";")[0]
        return status, json.loads(reply.read())

    def test_search_add_replay_quantity_remove_and_resume(self):
        status, session = self.request("sessions", {})
        self.assertEqual(status, 201)
        self.assertEqual(
            self.request("sessions", {})[1]["session_id"], session["session_id"]
        )
        status, result = self.request(
            "search", {"query": "backpack", "category": "backpack", "currency": "INR"}
        )
        self.assertEqual(status, 200)
        item = result["items"][0]
        body = {
            "operation_id": str(uuid.uuid4()),
            "variant_id": item["variant_id"],
            "quantity": 1,
            "currency": "INR",
            "revision": item["revision"],
            "unit_price_minor": item["price_minor"],
        }
        self.assertEqual(self.request("cart/add", body)[1]["code"], "added")
        self.assertEqual(self.request("cart/add", body)[1]["code"], "added")
        self.assertEqual(self.request("cart")[1]["items"][0]["quantity"], 1)
        changed = {**body, "quantity": 2}
        self.assertEqual(self.request("cart/add", changed)[0], 409)
        self.assertEqual(
            self.request(
                "cart/quantity",
                {
                    "operation_id": body["operation_id"],
                    "variant_id": item["variant_id"],
                    "quantity": 0,
                    "currency": "INR",
                },
            )[0],
            409,
        )
        update = {
            "operation_id": str(uuid.uuid4()),
            "variant_id": item["variant_id"],
            "quantity": 2,
            "currency": "INR",
        }
        self.assertEqual(self.request("cart/quantity", update)[1]["quantity"], 2)
        self.assertEqual(self.request("cart/quantity", update)[1]["quantity"], 2)
        update = {**update, "operation_id": str(uuid.uuid4()), "quantity": 0}
        self.assertEqual(self.request("cart/quantity", update)[1]["quantity"], 0)
        self.assertEqual(self.request("cart")[1]["items"], [])
        self.assertEqual(
            CartManagement(self.database).receipt(
                session["session_id"], update["operation_id"]
            )["status"],
            "committed",
        )

    def test_unauthenticated_invalid_quantity_and_unknown_voice(self):
        self.assertEqual(self.request("cart")[0], 403)
        self.request("sessions", {})
        self.assertEqual(
            self.request(
                "cart/quantity",
                {
                    "operation_id": str(uuid.uuid4()),
                    "variant_id": "v-best",
                    "quantity": True,
                    "currency": "INR",
                },
            )[0],
            400,
        )
        self.assertEqual(self.request("transcribe", {"pcm_base64": "AAAAAA=="})[0], 503)
        self.assertEqual(self.request("search", {"query": "x", "limit": 101})[0], 400)

    def test_discovery_cannot_silently_drop_a_text_price_boundary(self):
        self.request("sessions", {})
        body = {"query": "backpack under 20 rupees", "currency": "INR"}
        self.assertEqual(self.request("search", body)[0], 400)
        self.assertEqual(
            self.request("search", {**body, "under_minor": 2000, "inclusive": True})[0],
            400,
        )
        self.assertEqual(
            self.request("search", {**body, "under_minor": "2000", "inclusive": False})[
                0
            ],
            200,
        )

    def test_cancelled_asr_final_cannot_reappear_or_mutate(self):
        from dataclasses import replace
        from pathlib import Path

        from voicecart.audio import Transcript, TranscriptKind
        from voicecart.voice import FileArtifact

        entered = threading.Event()
        cancelled_seen = threading.Event()

        class BlockingRecognizer:
            def transcribe(self, pcm, turn, *, cancelled):
                entered.set()
                if cancelled.wait(3):
                    cancelled_seen.set()
                return Transcript(TranscriptKind.FINAL, "STALE TEST TRANSCRIPT", turn)

        web = self.server.application
        web.merchants["local"].settings = replace(
            web.merchants["local"].settings,
            asr=FileArtifact(Path("TEST-ONLY-NOT-LOADED"), "a" * 64),
        )
        web.recognizers["local"] = BlockingRecognizer()
        self.request("sessions", {})
        cookie = self.cookie
        result = []

        def transcribe():
            client = http.client.HTTPConnection(*self.server.server_address, timeout=5)
            try:
                client.request(
                    "POST",
                    "/api/local/transcribe",
                    body=json.dumps({"pcm_base64": "AAAAAA=="}),
                    headers={"Cookie": cookie, "Content-Type": "application/json"},
                )
                reply = client.getresponse()
                result.append((reply.status, json.loads(reply.read())))
            finally:
                client.close()

        thread = threading.Thread(target=transcribe)
        thread.start()
        self.assertTrue(entered.wait(2))
        self.assertEqual(self.request("cancel", {})[0], 200)
        thread.join(4)
        self.assertTrue(cancelled_seen.is_set())
        self.assertEqual(result[0][0], 409)
        self.assertNotIn("STALE TEST TRANSCRIPT", str(result))
        self.assertEqual(self.request("cart")[1]["items"], [])

    def test_unknown_historical_inventory_never_enables_add(self):
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE variants SET available=NULL,stock_quantity=NULL,price_freshness='stale'"
            )
        self.request("sessions", {})
        result = self.request("search", {"query": "backpack", "currency": "INR"})[1]
        self.assertFalse(any(row["can_add"] for row in result["items"]))
        row = result["items"][0]
        body = {
            "operation_id": str(uuid.uuid4()),
            "variant_id": row["variant_id"],
            "quantity": 1,
            "currency": "INR",
            "revision": row["revision"],
            "unit_price_minor": row["price_minor"],
        }
        self.assertEqual(self.request("cart/add", body)[0], 409)
        self.assertEqual(self.request("cart")[1]["items"], [])
