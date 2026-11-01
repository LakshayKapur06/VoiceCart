"""Bounded same-origin HTTP boundary over the existing VoiceCart core."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
from dataclasses import dataclass, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import psycopg

from voicecart.cli import components
from voicecart.database import DatabaseUnavailable
from voicecart.http_security import AccessDenied, Capabilities, RateLimiter, tenant_id
from voicecart.local_http import strict_json
from voicecart.settings import Settings


@dataclass
class Merchant:
    settings: Settings
    admin_hash: str
    currency: str = "INR"


class WebApplication:
    def __init__(self, merchants: dict[str, Merchant], secret: bytes):
        self.auth = Capabilities(secret)
        self.limiter = RateLimiter()
        self.merchants = merchants
        self.apps = {}
        used = set()
        for name, merchant in merchants.items():
            tenant_id(name)
            database, encoder, app = components(merchant.settings)
            config = database._config
            identity = (config["host"], config.get("port", "5432"), config["dbname"])
            if identity in used:
                raise ValueError("Each merchant requires a separate database")
            used.add(identity)
            database.check_ready()
            self.apps[name] = app

    @classmethod
    def from_env(cls):
        settings = Settings.from_env()
        secret = Path(os.environ["VOICECART_HTTP_SECRET_FILE"]).read_bytes().strip()
        registry = os.environ.get("VOICECART_TENANTS_FILE")
        if registry:
            raw = strict_json(Path(registry).read_text())
        else:
            raw = {
                "local": {
                    "database_url": settings.database_url,
                    "admin_token_file": os.environ["VOICECART_ADMIN_TOKEN_FILE"],
                    "currency": os.environ.get("VOICECART_CURRENCY", "INR"),
                }
            }
        merchants = {}
        for name, entry in raw.items():
            token = Path(entry["admin_token_file"]).read_text().strip()
            if len(token) < 32:
                raise ValueError("Admin token must have at least 32 characters")
            merchants[name] = Merchant(
                replace(settings, database_url=entry["database_url"]),
                hashlib.sha256(token.encode()).hexdigest(),
                entry.get("currency", "INR"),
            )
        return cls(merchants, secret)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, application):
        self.application = application
        self.slots = threading.BoundedSemaphore(24)
        super().__init__(address, Handler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server: Server

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, *args):
        # No raw paths, transcripts, authorization headers or user content.
        return

    def reply(
        self,
        status,
        payload,
        *,
        headers=None,
        content_type="application/json; charset=utf-8",
    ):
        body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload, default=str, allow_nan=False).encode()
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' https://m.media-amazon.com; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        length = self.headers.get("Content-Length", "")
        if not length.isdecimal() or not 0 < int(length) <= 2 * 1024 * 1024:
            raise ValueError("Request body must be 1–2097152 bytes")
        if self.headers.get_content_type() != "application/json":
            raise ValueError("JSON required")
        raw = strict_json(self.rfile.read(int(length)).decode())
        if not isinstance(raw, dict):
            raise ValueError("JSON object required")
        return raw

    def handle_request(self):
        try:
            origin = self.headers.get("Origin")
            expected = os.environ.get("VOICECART_PUBLIC_ORIGIN") or "http://" + str(
                self.server.server_address[0]
            ) + ":" + str(self.server.server_address[1])
            if (
                self.headers.get("Host", "").casefold()
                != urlsplit(expected).netloc.casefold()
            ):
                raise AccessDenied("Untrusted host")
            if origin and origin != expected:
                raise AccessDenied("Cross-origin access is disabled")
            if not self.server.application.limiter.allow(
                (self.client_address[0], "all")
            ):
                return self.reply(429, {"error": "Rate limit; retry later"})
            return self.route()
        except AccessDenied:
            self.reply(403, {"error": "Access denied or session expired"})
        except (ValueError, TypeError, KeyError, UnicodeError):
            self.reply(400, {"error": "Invalid request; check fields and limits"})
        except (DatabaseUnavailable, psycopg.Error):
            self.reply(
                503,
                {
                    "error": "Database unavailable; retain original operation ID for reconciliation"
                },
            )
        except Exception:
            self.reply(
                503,
                {
                    "error": "Operation unavailable; do not repeat a mutation with a new operation ID"
                },
            )

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def route(self):
        path = urlsplit(self.path).path
        if self.command == "GET" and path == "/health":
            for app in self.server.application.apps.values():
                app.database.check_ready()
            return self.reply(
                200,
                {
                    "status": "ok",
                    "service": "voicecart",
                    "merchant_count": len(self.server.application.apps),
                },
            )
        return self.reply(404, {"error": "Unknown endpoint"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    application = WebApplication.from_env()
    with Server((args.host, args.port), application) as server:
        print(
            f"VoiceCart HTTP on {args.host}:{args.port}; configure TLS at the deployment proxy.",
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()
