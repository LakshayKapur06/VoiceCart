"""Real scoped administration and actual-event analytics, test DB only."""

import hashlib
import http.client
import json
import os
import threading
import unittest

from tests.database_support import fabricated_document, isolated_database
from voicecart.events import EventStore
from voicecart.ingestion import parse_import
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings

TOKEN = "TEST-ONLY-ADMIN-KEY-DO-NOT-USE-OUTSIDE-TESTS"


class AdminHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute(
                "TRUNCATE sessions,variant_search,variants,products,application_events CASCADE"
            )
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',populated=false"
            )
        self.database.publish(parse_import(fabricated_document()))
        app = WebApplication(
            {
                "local": Merchant(
                    Settings(os.environ["VOICECART_TEST_DSN"]),
                    hashlib.sha256(TOKEN.encode()).hexdigest(),
                )
            },
            b"x" * 32,
            environment="test",
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

    def request(self, resource, body=None, headers=None):
        self.client.request(
            "POST" if body is not None else "GET",
            "/api/local/admin/" + resource,
            body=json.dumps(body) if body is not None else None,
            headers={
                "Content-Type": "application/json",
                "Cookie": self.cookie,
                **(headers or {}),
            },
        )
        reply = self.client.getresponse()
        status = reply.status
        if reply.getheader("Set-Cookie"):
            self.cookie = reply.getheader("Set-Cookie").split(";")[0]
        return status, json.loads(reply.read())

    def test_roles_login_export_atomic_edit_conflict_and_metrics(self):
        self.assertEqual(self.request("export")[0], 403)
        self.assertEqual(self.request("login", {"token": "bad"})[0], 403)
        self.assertEqual(self.request("login", {"token": TOKEN})[0], 200)
        document = self.request("export")[1]["snapshot"]
        document["previous_revision"] = document["revision"]
        document["revision"] = "admin-test-2"
        document["products"][0]["name"] = "Updated fixture title"
        self.assertEqual(self.request("import", document)[0], 200)
        self.assertEqual(
            self.request("import", document)[0], 400
        )  # stale CAS conflict safely rejects
        self.assertEqual(self.database.inspect()["revision"], "admin-test-2")
        analytics = self.request("analytics")[1]
        self.assertEqual(analytics["environment"], "test")
        self.assertEqual(analytics["coverage"]["variants"], 3)
        self.assertIn("Not collected", analytics["popular_queries"])
        self.assertEqual(self.request("health")[1]["database"], "ok")
        self.assertGreaterEqual(len(self.request("imports")[1]["imports"]), 1)
        self.request("logout", {})
        self.assertEqual(self.request("export")[0], 403)

    def test_duplicate_import_rolls_back_and_bearer_enforced(self):
        self.assertEqual(
            self.request("export", headers={"Authorization": "Bearer bad"})[0], 403
        )
        document = self.request("export", headers={"Authorization": "Bearer " + TOKEN})[
            1
        ]["snapshot"]
        document["previous_revision"] = document["revision"]
        document["revision"] = "invalid-test"
        document["products"].append(document["products"][0])
        status, result = self.request(
            "import", document, headers={"Authorization": "Bearer " + TOKEN}
        )
        self.assertEqual(status, 400)
        self.assertTrue(result["issues"])
        self.assertEqual(self.database.inspect()["revision"], "fixture-1")

    def test_create_variant_and_deactivate_preserve_source_contract(self):
        headers = {"Authorization": "Bearer " + TOKEN}
        document = self.request("export", headers=headers)[1]["snapshot"]
        document["previous_revision"] = document["revision"]
        document["revision"] = "create-test"
        document["products"].append(
            {
                "product_id": "TEST-CREATED",
                "name": "Fabricated admin test product",
                "category": "test-only",
            }
        )
        document["variants"].append(
            {
                "variant_id": "TEST-CREATED-V",
                "product_id": "TEST-CREATED",
                "price": {"minor_units": 1234, "currency": "INR"},
                "available": True,
                "stock_quantity": 1,
                "price_freshness": "current",
            }
        )
        self.assertEqual(self.request("import", document, headers=headers)[0], 200)
        self.assertEqual(self.database.inspect()["product_count"], 4)
        updated = self.request("export", headers=headers)[1]["snapshot"]
        updated["previous_revision"] = updated["revision"]
        updated["revision"] = "deactivate-test"
        next(row for row in updated["products"] if row["product_id"] == "TEST-CREATED")[
            "active"
        ] = False
        self.assertEqual(self.request("import", updated, headers=headers)[0], 200)
        self.assertEqual(
            self.request("catalogue", {"category": "test-only"}, headers=headers)[1][
                "total"
            ],
            0,
        )

    def test_event_privacy_environment_and_retention(self):
        events = EventStore(self.database, "test")
        events.record("search", "200", 0.01, [{"stage": "nlu.total", "seconds": 0.001}])
        summary = events.summary()
        self.assertEqual(summary["events"][0]["count"], 1)
        self.assertNotIn("query", str(summary["events"]))
        self.assertEqual(EventStore(self.database, "merchant").summary()["events"], [])
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE application_events SET occurred_at=now()-interval '8 days'"
            )
        events.cleanup(7)
        self.assertEqual(events.summary()["events"], [])
