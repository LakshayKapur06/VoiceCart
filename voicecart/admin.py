"""Scoped admin authentication, atomic full-catalogue management and real metrics."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import UTC, datetime

from voicecart.browse import CatalogueBrowser
from voicecart.database import PublicationConflict
from voicecart.events import EventStore
from voicecart.http_security import AccessDenied
from voicecart.ingestion import ImportValidationError, parse_import
from voicecart.local_http import LocalJSONClient, verify_model
from voicecart.web_api import cookie, minor_units


def authorized(handler, tenant):
    web = handler.server.application
    token = handler.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        supplied = hashlib.sha256(token[7:].encode()).hexdigest()
        if hmac.compare_digest(supplied, web.merchants[tenant].admin_hash):
            return
        raise AccessDenied("Invalid merchant credential")
    web.auth.from_cookie(handler.headers.get("Cookie"), tenant, "admin")


def export_catalogue(database):
    with database.connect() as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        state = connection.execute(
            "SELECT * FROM catalogue_state WHERE singleton=true"
        ).fetchone()
        products = list(
            connection.execute("SELECT * FROM products ORDER BY product_id")
        )
        variants = []
        for row in connection.execute("SELECT * FROM variants ORDER BY variant_id"):
            fields = dict(row)
            price = fields.pop("price_minor")
            currency = fields.pop("currency")
            fields["price"] = (
                {"minor_units": price, "currency": currency}
                if price is not None
                else None
            )
            variants.append(fields)
        metadata = {
            row["product_id"]: row["payload"]
            for row in connection.execute("SELECT * FROM product_metadata")
        }
    return {
        "schema_version": 1,
        "revision": state["revision"],
        "previous_revision": state["revision"],
        "coverage": state["coverage"],
        "source": state["source"] or "",
        "valid_until": state["valid_until"].isoformat() if state["valid_until"] else "",
        "products": products,
        "variants": variants,
        "metadata": metadata,
        "aliases": state["aliases"],
    }


def admin(handler, tenant, resource):
    web = handler.server.application
    app = web.apps[tenant]
    if resource == "login" and handler.command == "POST":
        if not web.limiter.allow(
            (handler.client_address[0], tenant, "admin-login"), 10
        ):
            return handler.reply(429, {"error": "Authentication rate limit"})
        token = handler.body().get("token")
        if (
            not isinstance(token, str)
            or not 32 <= len(token) <= 256
            or not hmac.compare_digest(
                hashlib.sha256(token.encode()).hexdigest(),
                web.merchants[tenant].admin_hash,
            )
        ):
            raise AccessDenied("Invalid administrator credential")
        return handler.reply(
            200,
            {"authenticated": True, "merchant": tenant},
            headers=cookie(handler, tenant, "admin", str(uuid.uuid4()), 1800),
        )
    if resource == "logout" and handler.command == "POST":
        return handler.reply(
            200,
            {"authenticated": False},
            headers={
                "Set-Cookie": f"vca_{tenant}=; Path=/api/{tenant}/; HttpOnly; SameSite=Strict; Max-Age=0"
            },
        )
    authorized(handler, tenant)
    if resource == "catalogue" and handler.command == "POST":
        body = handler.body()
        return handler.reply(
            200,
            CatalogueBrowser(app.database).search(
                body.get("query", ""),
                brand=body.get("brand", ""),
                category=body.get("category", ""),
                currency=body.get("currency"),
                offset=body.get("offset", 0),
                limit=body.get("limit", 24),
            ),
        )
    if resource == "export" and handler.command == "GET":
        return handler.reply(200, {"snapshot": export_catalogue(app.database)})
    if resource == "import" and handler.command == "POST":
        body = handler.body()
        variants = body.get("variants")
        if not isinstance(variants, list):
            raise ValueError("Variants must be an array")
        for row in variants:
            if not isinstance(row, dict) or (
                row.get("price") is not None and not isinstance(row["price"], dict)
            ):
                raise ValueError("Variant and price must be objects")
            if row.get("price") is not None:
                row["price"]["minor_units"] = minor_units(row["price"]["minor_units"])
            if isinstance(row.get("stock_quantity"), str):
                row["stock_quantity"] = minor_units(row["stock_quantity"])
        try:
            bundle = parse_import(body)
        except ImportValidationError as error:
            return handler.reply(
                400,
                {"error": "Catalogue validation failed", "issues": list(error.issues)},
            )
        try:
            revision = web.adapters[tenant].synchronize(bundle)
        except PublicationConflict:
            return handler.reply(
                400,
                {
                    "error": "Catalogue changed; reload the current revision before publishing."
                },
            )
        return handler.reply(
            200,
            {
                "revision": revision,
                "products": len(bundle.products),
                "variants": len(bundle.variants),
                "committed": True,
            },
        )
    if resource == "imports" and handler.command == "GET":
        with app.database.connect() as connection:
            rows = list(
                connection.execute(
                    "SELECT * FROM import_history ORDER BY import_id DESC LIMIT 100"
                )
            )
        return handler.reply(200, {"imports": rows})
    if resource == "analytics" and handler.command == "GET":
        return handler.reply(200, EventStore(app.database, web.environment).summary())
    if resource == "health" and handler.command == "GET":
        state = app.database.inspect()
        settings = web.merchants[tenant].settings
        model = "unconfigured"
        if settings.nlu_model:
            try:
                verify_model(
                    LocalJSONClient(settings.ollama_url, timeout=2),
                    settings.nlu_model,
                    settings.nlu_digest,
                )
                model = "pinned local model present"
            except Exception:
                model = "unavailable or identity mismatch"
        return handler.reply(
            200,
            {
                "database": "ok",
                "catalogue_revision": state["revision"],
                "catalogue_populated": state["populated"],
                "catalogue_expired": state["valid_until"] is None
                or state["valid_until"] <= datetime.now(UTC),
                "inference": model,
                "environment": web.environment,
                "telemetry_write_failures": web.telemetry_failures,
                "acoustic_devices": "Not measured by HTTP health",
            },
        )
    return handler.reply(404, {"error": "Unknown administrator operation"})
