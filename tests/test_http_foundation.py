"""Security partitions and real loopback HTTP/PostgreSQL foundation."""

import hashlib
import http.client
import json
import os
import threading
import unittest
from unittest.mock import patch

from tests.database_support import isolated_database
from voicecart.database import parse_local_dsn
from voicecart.http_security import AccessDenied, Capabilities, RateLimiter
from voicecart.local_http import LocalJSONClient
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings


class SecurityTests(unittest.TestCase):
    def test_capability_equivalence_tampering_roles_tenants_and_expiry(self):
        auth = Capabilities(b"x" * 32)
        token = auth.issue("one", "session", "customer")
        self.assertEqual(auth.verify(token, "one", "customer"), "session")
        for value, tenant, role in [
            (token + "x", "one", "customer"),
            (token, "two", "customer"),
            (token, "one", "admin"),
            ("broken", "one", "customer"),
            (auth.issue("one", "session", "customer", ttl=-1), "one", "customer"),
        ]:
            with (
                self.subTest(tenant=tenant, role=role),
                self.assertRaises(AccessDenied),
            ):
                auth.verify(value, tenant, role)
        with self.assertRaises(ValueError):
            Capabilities(b"short")

    def test_rate_limit_boundaries_and_bounded_storage(self):
        rate = RateLimiter()
        self.assertTrue(rate.allow(("test",), 1, now=0))
        self.assertFalse(rate.allow(("test",), 1, now=59.999))
        self.assertTrue(rate.allow(("test",), 1, now=60))
        for index in range(5000):
            rate.allow((index,), now=60)
        self.assertLessEqual(len(rate.windows), 4096)

    def test_trusted_service_hosts_are_explicit_and_not_default(self):
        with self.assertRaises(ValueError):
            parse_local_dsn("postgresql://db/test")
        with patch.dict(
            os.environ,
            VOICECART_TRUSTED_DATABASE_HOSTS="db",
            VOICECART_TRUSTED_INFERENCE_HOSTS="host.docker.internal",
        ):
            self.assertEqual(parse_local_dsn("postgresql://db/test")["host"], "db")
            LocalJSONClient("http://host.docker.internal:11434")
        with self.assertRaises(ValueError):
            LocalJSONClient("http://host.docker.internal:11434")


class HTTPFoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def test_health_origin_host_and_no_fake_endpoints(self):
        settings = Settings(os.environ["VOICECART_TEST_DSN"])
        application = WebApplication(
            {
                "local": Merchant(
                    settings, hashlib.sha256(b"not-a-real-admin-key").hexdigest()
                )
            },
            b"x" * 32,
        )
        server = Server(("127.0.0.1", 0), application)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = http.client.HTTPConnection(*server.server_address, timeout=3)
            client.request("GET", "/health")
            reply = client.getresponse()
            self.assertEqual(reply.status, 200)
            self.assertEqual(json.loads(reply.read())["status"], "ok")
            client.request(
                "POST",
                "/not-real",
                body="{}",
                headers={
                    "Content-Type": "application/json",
                    "Origin": "https://evil.invalid",
                },
            )
            reply = client.getresponse()
            self.assertEqual(reply.status, 403)
            reply.read()
            client.request("GET", "/health", headers={"Host": "evil.invalid"})
            reply = client.getresponse()
            self.assertEqual(reply.status, 403)
            reply.read()
            client.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)

    def test_duplicate_database_tenants_rejected(self):
        settings = Settings(os.environ["VOICECART_TEST_DSN"])
        with self.assertRaises(ValueError):
            WebApplication(
                {
                    "one": Merchant(settings, "a" * 64),
                    "two": Merchant(settings, "b" * 64),
                },
                b"x" * 32,
            )
