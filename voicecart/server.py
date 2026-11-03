"""Bounded same-origin HTTP boundary over the existing VoiceCart core."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import psycopg

from voicecart.cli import components
from voicecart.database import DatabaseUnavailable
from voicecart.domain import require_currency
from voicecart.events import EventStore
from voicecart.http_security import AccessDenied, Capabilities, RateLimiter, tenant_id
from voicecart.local_http import strict_json
from voicecart.merchant import LocalMerchantAdapter
from voicecart.sessions import SessionError
from voicecart.settings import Settings
from voicecart.telemetry import measurements


@dataclass
class Merchant:
    settings: Settings
    admin_hash: str
    currency: str = "INR"


class WebApplication:
    def __init__(
        self, merchants: dict[str, Merchant], secret: bytes, environment="development"
    ):
        if environment not in ("test", "development", "merchant"):
            raise ValueError("Invalid deployment environment")
        self.environment = environment
        self.telemetry_failures = 0
        self.auth = Capabilities(secret)
        self.limiter = RateLimiter()
        self.merchants = merchants
        self.apps = {}
        self.adapters = {}
        self.speech_lock = threading.Lock()
        self.recognizers: dict[str, Any] = {}
        self.synthesizers: dict[str, Any] = {}
        if not 1 <= len(merchants) <= 16:
            raise ValueError("Configure 1–16 explicitly isolated merchants")
        used = set()
        for name, merchant in merchants.items():
            tenant_id(name)
            require_currency(merchant.currency)
            if len(merchant.admin_hash) != 64 or any(
                c not in "0123456789abcdef" for c in merchant.admin_hash
            ):
                raise ValueError("Invalid administrator credential hash")
            database, encoder, app = components(merchant.settings)
            config = database._config
            identity = (config["host"], config.get("port", "5432"), config["dbname"])
            if identity in used:
                raise ValueError("Each merchant requires a separate database")
            used.add(identity)
            database.check_ready()
            self.apps[name] = app
            self.adapters[name] = LocalMerchantAdapter(app)

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
            if not 32 <= len(token) <= 256:
                raise ValueError("Admin token must have 32–256 characters")
            merchants[name] = Merchant(
                replace(settings, database_url=entry["database_url"]),
                hashlib.sha256(token.encode()).hexdigest(),
                entry.get("currency", "INR"),
            )
        return cls(
            merchants, secret, os.environ.get("VOICECART_ENVIRONMENT", "development")
        )


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, application):
        self.application = application
        self.slots = threading.BoundedSemaphore(24)
        self.next_cleanup = time.monotonic() + 60
        super().__init__(address, Handler)

    def service_actions(self):
        if time.monotonic() < self.next_cleanup:
            return
        self.next_cleanup = time.monotonic() + 60
        for app in self.application.apps.values():
            try:
                app.sessions.cleanup_expired()
                with app._guard:
                    candidates = list(
                        set(app._last) | set(app._events) | set(app._turns)
                    )
                if candidates:
                    with app.database.connect() as connection:
                        active = {
                            str(row["session_id"])
                            for row in connection.execute(
                                "SELECT session_id FROM sessions WHERE session_id=ANY(%s::uuid[]) AND expires_at>now()",
                                (candidates,),
                            )
                        }
                    for identity in set(candidates) - active:
                        app.forget(identity)
                EventStore(app.database, self.application.environment).cleanup(
                    int(os.environ.get("VOICECART_EVENT_RETENTION_DAYS", "7"))
                )
            except Exception:
                self.application.telemetry_failures += 1

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
        def precise(value):
            if isinstance(value, dict):
                return {key: precise(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [precise(item) for item in value]
            if type(value) is int and abs(value) > 2**53 - 1:
                return str(value)
            return value

        body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(precise(payload), default=str, allow_nan=False).encode()
        )
        self.response_status = status
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
        if (
            self.headers.get("Transfer-Encoding")
            or len(self.headers.get_all("Content-Length", [])) != 1
        ):
            raise ValueError(
                "One explicit Content-Length and no transfer encoding required"
            )
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
        start = time.perf_counter()
        with measurements() as trace:
            try:
                return self._handle_request()
            finally:
                parts = urlsplit(self.path).path.strip("/").split("/")
                if (
                    len(parts) >= 3
                    and parts[0] == "api"
                    and parts[1] in self.server.application.apps
                ):
                    resource = "/".join(parts[2:])
                    kinds = {
                        "search": "search",
                        "query": "nlu",
                        "cart/add": "cart.add",
                        "cart/quantity": "cart.adjust",
                        "transcribe": "asr",
                        "speak": "tts",
                        "admin/import": "import",
                        "admin/login": "admin.auth",
                    }
                    if resource in kinds:
                        try:
                            EventStore(
                                self.server.application.apps[parts[1]].database,
                                self.server.application.environment,
                            ).record(
                                kinds[resource],
                                str(getattr(self, "response_status", 503)),
                                time.perf_counter() - start,
                                trace.spans,
                            )
                        except Exception:
                            self.server.application.telemetry_failures += 1

    def _handle_request(self):
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
        except (AccessDenied, SessionError):
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
        from voicecart.web_api import dispatch

        if dispatch(self):
            return None
        if self.command == "GET" and path in (
            "/",
            "/admin",
            "/app.js",
            "/admin.js",
            "/style.css",
        ):
            from importlib import resources

            filename = {"/": "index.html", "/admin": "admin.html"}.get(
                path, path.lstrip("/")
            )
            asset = resources.files("voicecart").joinpath("web", filename)
            if asset.is_file():
                content_type = (
                    "text/html; charset=utf-8"
                    if filename.endswith(".html")
                    else "text/css"
                    if filename.endswith(".css")
                    else "text/javascript"
                )
                return self.reply(200, asset.read_bytes(), content_type=content_type)
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
