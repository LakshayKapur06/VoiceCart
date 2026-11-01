"""Common adapter and real separate-database merchant isolation contracts."""

import hashlib
import http.client
import json
import os
import threading
import unittest
import uuid

from psycopg.conninfo import make_conninfo

from tests.database_support import (
    fabricated_document,
    isolated_database,
    isolated_peer_database,
)
from voicecart.application import ShoppingApplication
from voicecart.ingestion import parse_import
from voicecart.merchant import AddIntent, LocalMerchantAdapter
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings

TOKEN = "TEST-ONLY-MERCHANT-ONE-CREDENTIAL-DO-NOT-USE"


class MerchantTests(unittest.TestCase):
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

    def test_adapter_exact_snapshot_add_replay_refresh_and_operation(self):
        app = ShoppingApplication(self.database, None)
        adapter = LocalMerchantAdapter(app)
        session = app.sessions.create()
        operation = str(uuid.uuid4())
        intent = AddIntent(operation, "v-best", 1, "INR", "fixture-1", 150000)
        first = adapter.add(session, intent)
        second = adapter.add(session, intent)
        self.assertEqual(first, second)
        self.assertEqual(adapter.cart(session)["items"][0]["quantity"], 1)
        self.assertEqual(adapter.operation(session, operation)["status"], "committed")
        self.assertEqual(adapter.lookup("p-best")["revision"], "fixture-1")
        self.assertEqual(
            adapter.refresh_offers(["v-best"])[0]["offer"]["price"]["minor_units"],
            150000,
        )
        self.assertEqual(
            adapter.operation(session, str(uuid.uuid4()))["status"], "unknown"
        )

    def test_real_tenant_database_auth_session_and_catalogue_isolation(self):
        with isolated_peer_database() as peer:
            raw = fabricated_document()
            raw["products"][0]["name"] = "Other tenant test-only product"
            peer.publish(parse_import(raw))
            first = Merchant(
                Settings(os.environ["VOICECART_TEST_DSN"]),
                hashlib.sha256(TOKEN.encode()).hexdigest(),
            )
            second_token = "TEST-ONLY-MERCHANT-TWO-CREDENTIAL-DO-NOT-USE"
            second = Merchant(
                Settings(
                    make_conninfo(
                        os.environ["VOICECART_TEST_DSN"], dbname=peer._config["dbname"]
                    )
                ),
                hashlib.sha256(second_token.encode()).hexdigest(),
            )
            web = WebApplication(
                {"one": first, "two": second}, b"x" * 32, environment="test"
            )
            server = Server(("127.0.0.1", 0), web)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            client = http.client.HTTPConnection(*server.server_address, timeout=5)

            def request(tenant, resource, body, token):
                client.request(
                    "POST",
                    f"/api/{tenant}/merchant/{resource}",
                    body=json.dumps(body),
                    headers={
                        "Authorization": "Bearer " + token,
                        "Content-Type": "application/json",
                    },
                )
                reply = client.getresponse()
                return reply.status, json.loads(reply.read())

            try:
                self.assertEqual(request("two", "sessions", {}, TOKEN)[0], 403)
                status, result = request("one", "sessions", {}, TOKEN)
                self.assertEqual(status, 201)
                self.assertEqual(
                    request(
                        "two",
                        "cart",
                        {"session_id": result["session_id"]},
                        second_token,
                    )[0],
                    409,
                )
                self.assertEqual(
                    request("two", "lookup", {"product_id": "p-best"}, second_token)[1][
                        "product"
                    ]["name"],
                    "Other tenant test-only product",
                )
                self.assertEqual(
                    request("one", "lookup", {"product_id": "p-best"}, TOKEN)[1][
                        "product"
                    ]["name"],
                    "College backpack",
                )
            finally:
                client.close()
                server.shutdown()
                server.server_close()
                thread.join(2)
