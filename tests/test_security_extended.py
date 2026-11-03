"""Actual HTTP negative authorization/framing/config/recovery regressions."""

import http.client
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_web_customer as customer_tests
from voicecart.database import DatabaseUnavailable
from voicecart.http_security import AccessDenied, Capabilities
from voicecart.server import WebApplication


class ExtendedSecurityTests(unittest.TestCase):
    setUpClass = classmethod(customer_tests.CustomerHTTPTests.setUpClass.__func__)
    setUp = customer_tests.CustomerHTTPTests.setUp
    tearDown = customer_tests.CustomerHTTPTests.tearDown
    request = customer_tests.CustomerHTTPTests.request

    def raw(self, path, method="POST", body="{}", headers=None):
        client = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            client.request(
                method,
                path,
                body=body,
                headers={
                    "Content-Type": "application/json",
                    "Cookie": self.cookie,
                    **(headers or {}),
                },
            )
            reply = client.getresponse()
            return reply.status, dict(reply.getheaders()), json.loads(reply.read())
        finally:
            client.close()

    def test_every_protected_route_requires_correct_role(self):
        customers = {
            "POST": [
                "turns",
                "search",
                "query",
                "ack",
                "cancel",
                "repeat",
                "transcribe",
                "speak",
                "cart/add",
                "cart/quantity",
                "cart/retry",
            ],
            "GET": ["cart", "operations"],
        }
        for method, resources in customers.items():
            for name in resources:
                with self.subTest(name=name):
                    self.assertEqual(self.raw("/api/local/" + name, method)[0], 403)
        admins = {
            "POST": ["catalogue", "import"],
            "GET": ["export", "imports", "analytics", "health"],
        }
        for method, resources in admins.items():
            for name in resources:
                with self.subTest(admin=name):
                    self.assertEqual(
                        self.raw("/api/local/admin/" + name, method)[0], 403
                    )
        merchants = [
            "sessions",
            "search",
            "lookup",
            "refresh",
            "cart",
            "add",
            "quantity",
            "operation",
        ]
        self.request("sessions", {})
        for name in merchants:
            with self.subTest(merchant=name):
                self.assertEqual(self.raw("/api/local/merchant/" + name)[0], 403)
        self.assertEqual(self.raw("/api/local/admin/export", "GET")[0], 403)

    def test_cookie_scope_https_flag_origin_cors_and_expiry(self):
        port = self.server.server_address[1]
        origin = f"https://localhost:{port}"
        with patch.dict(os.environ, VOICECART_PUBLIC_ORIGIN=origin):
            status, headers, _ = self.raw(
                "/api/local/sessions",
                headers={"Host": f"localhost:{port}", "Origin": origin},
            )
            self.assertEqual(status, 201)
            self.assertIn("Secure", headers["Set-Cookie"])
            self.assertIn("HttpOnly", headers["Set-Cookie"])
            self.assertIn("SameSite=Strict", headers["Set-Cookie"])
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertEqual(
                self.raw(
                    "/api/local/sessions",
                    headers={"Host": f"localhost:{port}", "Origin": "null"},
                )[0],
                403,
            )
        self.request("sessions", {})
        identity = self.server.application.auth.from_cookie(
            self.cookie, "local", "customer"
        )
        with self.database.connect() as c:
            c.execute(
                "UPDATE sessions SET expires_at='2000-01-01' WHERE session_id=%s",
                (identity,),
            )
        self.assertEqual(self.request("cart")[0], 403)
        auth = Capabilities(b"x" * 32)
        old = auth.issue("local", "session", "customer")
        with self.assertRaises(AccessDenied):
            Capabilities(b"y" * 32).verify(old, "local", "customer")

    def test_compose_probe_matches_strict_host_policy(self):
        compose = (Path(__file__).resolve().parents[1] / "compose.yaml").read_text()
        self.assertIn("VOICECART_PUBLIC_ORIGIN: http://localhost:8080", compose)
        self.assertIn("urlopen('http://localhost:8080/health'", compose)
        port = self.server.server_address[1]
        with patch.dict(os.environ, VOICECART_PUBLIC_ORIGIN=f"http://localhost:{port}"):
            self.assertEqual(self.raw("/health", "GET")[0], 403)
            self.assertEqual(
                self.raw("/health", "GET", headers={"Host": f"localhost:{port}"})[0],
                200,
            )

    def test_body_limits_duplicate_json_and_framing_rejected(self):
        self.request("sessions", {})
        for body, headers in [
            ("[]", {}),
            ('{"query":1,"query":2}', {}),
            ("{}", {"Content-Type": "text/plain"}),
            ("{}", {"Content-Length": str(2 * 1024 * 1024 + 1)}),
            ("{}", {"Transfer-Encoding": "chunked"}),
        ]:
            with self.subTest(body=body, headers=headers):
                self.assertEqual(
                    self.raw("/api/local/search", body=body, headers=headers)[0], 400
                )

    def test_malformed_nested_admin_import_is_400_without_publication(self):
        before = self.database.inspect()["revision"]
        for variants in [None, {}, [1], [{"price": 1}], [{"price": []}]]:
            with self.subTest(variants=variants):
                status, _, _ = self.raw(
                    "/api/local/admin/import",
                    body=json.dumps({"variants": variants}),
                    headers={"Authorization": "Bearer TEST-ONLY-KEY"},
                )
                self.assertEqual(status, 400)
                self.assertEqual(self.database.inspect()["revision"], before)

    def test_health_outage_sanitized_and_missing_secrets_fail_startup(self):
        app = self.server.application.apps["local"]
        with patch.object(
            app.database,
            "check_ready",
            side_effect=DatabaseUnavailable("PRIVATE TEST SQL DETAIL"),
        ):
            status, _, payload = self.raw("/health", "GET")
            self.assertEqual(status, 503)
            self.assertNotIn("PRIVATE TEST SQL DETAIL", str(payload))
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaises((ValueError, KeyError)),
        ):
            WebApplication.from_env()
