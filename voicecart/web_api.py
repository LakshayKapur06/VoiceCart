"""Customer HTTP contracts; every mutation delegates to authoritative services."""

from __future__ import annotations

import base64
import io
import os
import uuid
import wave
from dataclasses import asdict
from urllib.parse import urlsplit

from voicecart.application import Response
from voicecart.browse import CatalogueBrowser
from voicecart.cart import AddCommand, CartError, OutcomeUnknown
from voicecart.cart_management import CartManagement
from voicecart.domain import (
    ExactIdentifier,
    HardConstraints,
    IdentifierKind,
    RetrievalRoute,
    SearchRequest,
)
from voicecart.http_security import AccessDenied
from voicecart.sessions import SessionError, uuid_text
from voicecart.voice import PiperSynthesizer, WhisperRecognizer


def minor_units(value):
    if (
        isinstance(value, str)
        and value.isascii()
        and value.isdecimal()
        and len(value) <= 19
    ):
        value = int(value)
    if type(value) is not int or not 0 <= value <= 2**63 - 1:
        raise ValueError("Integer minor units required")
    return value


def cookie(handler, tenant, role, identity, ttl=3600):
    secure = (
        "; Secure"
        if os.environ.get("VOICECART_PUBLIC_ORIGIN", "").startswith("https:")
        else ""
    )
    name = ("vca_" if role == "admin" else "vcc_") + tenant
    token = handler.server.application.auth.issue(tenant, identity, role, ttl=ttl)
    return {
        "Set-Cookie": f"{name}={token}; Path=/api/{tenant}/; HttpOnly; SameSite=Strict; Max-Age={ttl}{secure}"
    }


def session(handler, tenant):
    identity = handler.server.application.auth.from_cookie(
        handler.headers.get("Cookie"), tenant, "customer"
    )
    app = handler.server.application.apps[tenant]
    with app.database.connect() as connection:
        app.sessions.require(connection, identity)
    return identity


def customer(handler, tenant, resource):
    web = handler.server.application
    app = web.apps[tenant]
    method = handler.command
    if resource == "sessions" and method == "POST":
        if not web.limiter.allow((handler.client_address[0], tenant, "sessions"), 20):
            return handler.reply(429, {"error": "Session rate limit"})
        try:
            identity = session(handler, tenant)
            return handler.reply(
                200,
                {
                    "session_id": identity,
                    "merchant": tenant,
                    "currency": web.merchants[tenant].currency,
                },
            )
        except (AccessDenied, SessionError):
            app.sessions.cleanup_expired()
        identity = app.sessions.create()
        return handler.reply(
            201,
            {
                "session_id": identity,
                "merchant": tenant,
                "currency": web.merchants[tenant].currency,
            },
            headers=cookie(handler, tenant, "customer", identity),
        )
    identity = session(handler, tenant)
    management = CartManagement(app.database)
    operation = None
    try:
        if resource == "search" and method == "POST":
            body = handler.body()
            if app.cart.pending(identity):
                return handler.reply(
                    409,
                    {
                        "error": "Resolve the original pending operation before a new search."
                    },
                )
            result = CatalogueBrowser(app.database).search(
                body.get("query", ""),
                brand=body.get("brand", ""),
                category=body.get("category", ""),
                currency=body.get("currency"),
                under=minor_units(body["under_minor"])
                if body.get("under_minor") is not None
                else None,
                inclusive=body.get("inclusive", False),
                offset=body.get("offset", 0),
                limit=body.get("limit", 24),
            )
            # Public product responses exclude raw source videos/payload/user identifiers.
            for item in result["items"] + (
                [result["cheapest"]] if result["cheapest"] else []
            ):
                item["metadata"] = {
                    k: v
                    for k, v in item["metadata"].items()
                    if k
                    in (
                        "brand",
                        "attributes",
                        "images",
                        "source_url",
                        "source_record_id",
                        "source_revision",
                        "historical",
                        "raw_price",
                        "price_currency",
                        "variant_semantics",
                    )
                }
            turn = app.begin(identity)
            message = f"Found {result['total']} matching imported records. Prices and availability are labelled; historical data cannot authorize a cart add."
            app.remember(Response("results", message, identity, turn))
            return handler.reply(200, {**result, "message": message})
        if resource == "query" and method == "POST":
            body = handler.body()
            if (
                not isinstance(body.get("text"), str)
                or not 1 <= len(body["text"]) <= 4000
            ):
                raise ValueError("Invalid text")
            return handler.reply(200, asdict(app.text(identity, body["text"])))
        if resource == "cancel" and method == "POST":
            return handler.reply(200, asdict(app.cancel(identity)))
        if resource == "repeat" and method == "POST":
            return handler.reply(200, asdict(app.repeat(identity)))
        if resource == "ack" and method == "POST":
            body = handler.body()
            return handler.reply(
                200,
                {
                    "acknowledged": app.sessions.mark_presented(
                        identity, body["list_id"], body["turn_id"]
                    )
                },
            )
        if resource == "operations" and method == "GET":
            with app.database.connect() as connection:
                rows = list(
                    connection.execute(
                        "SELECT operation_id,status,created_at FROM commands WHERE session_id=%s ORDER BY created_at DESC LIMIT 10",
                        (identity,),
                    )
                )
            return handler.reply(200, {"operations": rows})
        if resource == "cart" and method == "GET":
            return handler.reply(200, management.overview(identity))
        if resource == "cart/add" and method == "POST":
            body = handler.body()
            operation = uuid_text(body["operation_id"])
            body["unit_price_minor"] = minor_units(body["unit_price_minor"])
            quantity = body.get("quantity", 1)
            if type(quantity) is not int or not 1 <= quantity <= 99:
                raise ValueError("Quantity 1–99 required")
            try:
                command = app.cart.load_command(identity, operation)
                if (
                    command.variant_id,
                    command.request.constraints.currency,
                    command.request.constraints.quantity,
                    command.expected_revision,
                    command.expected_unit_price_minor,
                ) != (
                    body["variant_id"],
                    body["currency"],
                    quantity,
                    body["revision"],
                    body["unit_price_minor"],
                ):
                    raise CartError("operation_identity_conflict")
            except CartError as error:
                if error.code != "unknown_operation":
                    raise
                turn = app.begin(identity)
                request = SearchRequest(
                    HardConstraints(body["currency"], quantity=quantity),
                    RetrievalRoute.EXACT,
                    ExactIdentifier(IdentifierKind.VARIANT_ID, body["variant_id"]),
                )
                command = AddCommand(
                    identity,
                    turn,
                    operation,
                    "exact",
                    request,
                    body["variant_id"],
                    body["revision"],
                    body["unit_price_minor"],
                )
                app.cart.prepare(command)
            receipt = app.cart.add(command)
            response = app.confirmed_receipt(identity, command.turn_id, receipt)
            return handler.reply(200, asdict(response))
        if resource == "cart/quantity" and method == "POST":
            body = handler.body()
            operation = body["operation_id"]
            receipt = management.set_quantity(
                identity,
                operation,
                body["variant_id"],
                body["quantity"],
                body["currency"],
            )
            return handler.reply(200, receipt)
        if resource == "cart/retry" and method == "POST":
            operation = handler.body()["operation_id"]
            receipt = management.receipt(identity, operation)
            if receipt:
                return handler.reply(200, receipt)
            return handler.reply(200, asdict(app.retry(identity, operation)))
        if resource == "transcribe" and method == "POST":
            body = handler.body()
            pcm = base64.b64decode(body["pcm_base64"], validate=True)
            if not 0 < len(pcm) <= 960000:
                raise ValueError("Capture at most 30 seconds")
            settings = web.merchants[tenant].settings
            if settings.asr is None:
                return handler.reply(
                    503, {"error": "Local ASR is not configured. Use text input."}
                )
            with web.speech_lock:
                recognizer = web.recognizers.setdefault(tenant, None)
                if recognizer is None:
                    recognizer = WhisperRecognizer(settings.asr)
                    web.recognizers[tenant] = recognizer
            transcript = recognizer.transcribe(pcm, str(uuid.uuid4()))
            return handler.reply(
                200,
                {
                    "text": transcript.text,
                    "requires_review": True,
                    "cart_mutated": False,
                },
            )
        if resource == "speak" and method == "POST":
            settings = web.merchants[tenant].settings
            if settings.voice is None or settings.voice_config is None:
                return handler.reply(
                    503,
                    {
                        "error": "Local speech output is not configured. Read the text response."
                    },
                )
            text = app.repeat(identity).text
            with web.speech_lock:
                synthesizer = web.synthesizers.get(tenant)
                if synthesizer is None:
                    synthesizer = PiperSynthesizer(
                        settings.voice, settings.voice_config
                    )
                    web.synthesizers[tenant] = synthesizer
            chunks = list(synthesizer.synthesize(text))
            if not chunks:
                raise ValueError("No speech")
            output = io.BytesIO()
            with wave.open(output, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(chunks[0].sample_rate_hz)
                wav.writeframes(b"".join(chunk.pcm_data for chunk in chunks))
            return handler.reply(200, output.getvalue(), content_type="audio/wav")
    except OutcomeUnknown:
        return handler.reply(
            409,
            {
                "error": "Outcome unknown. Retry the SAME operation ID.",
                "operation_id": operation,
            },
        )
    except (CartError, SessionError):
        return handler.reply(
            409,
            {
                "error": "Current offer/session/operation is invalid. No new mutation was confirmed; retain the original operation ID."
            },
        )
    raise ValueError("Unsupported customer operation")


def dispatch(handler):
    path = urlsplit(handler.path).path
    parts = path.strip("/").split("/")
    if len(parts) < 3 or parts[0] != "api":
        return False
    tenant = parts[1]
    if tenant not in handler.server.application.apps:
        raise AccessDenied("Unknown merchant")
    if parts[2] == "admin":
        from voicecart.admin import admin

        admin(handler, tenant, "/".join(parts[3:]))
    else:
        customer(handler, tenant, "/".join(parts[2:]))
    return True
