"""Customer HTTP contracts; every mutation delegates to authoritative services."""

from __future__ import annotations

import base64
import io
import os
import wave
from dataclasses import asdict
from urllib.parse import urlsplit

from voicecart.application import Response
from voicecart.audio import Transcript, TranscriptKind
from voicecart.cart import CartError, OutcomeUnknown
from voicecart.http_security import AccessDenied
from voicecart.nlu import BOUND, rupees_to_minor
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
    adapter = web.adapters[tenant]
    operation = None
    try:
        if resource == "turns" and method == "POST":
            if app.cart.pending(identity):
                return handler.reply(
                    409,
                    {
                        "error": "Resolve the original pending operation before a new turn."
                    },
                )
            return handler.reply(201, {"turn_id": app.begin(identity)})
        if resource == "search" and method == "POST":
            body = handler.body()
            if app.cart.pending(identity):
                return handler.reply(
                    409,
                    {
                        "error": "Resolve the original pending operation before a new search."
                    },
                )
            query = body.get("query", "")
            bounds = list(BOUND.finditer(query)) if isinstance(query, str) else []
            if bounds:
                expected_inclusive = bounds[0][1].casefold() not in (
                    "under",
                    "below",
                    "less than",
                )
                if (
                    len(bounds) != 1
                    or body.get("under_minor") is None
                    or minor_units(body["under_minor"]) != rupees_to_minor(bounds[0][2])
                    or body.get("inclusive", False) != expected_inclusive
                ):
                    return handler.reply(
                        400,
                        {
                            "error": "Match the price in your words using the maximum-price and boundary controls, or select Shopping assistant. Price instructions are not silently ignored."
                        },
                    )
            turn = (
                uuid_text(body["turn_id"])
                if body.get("turn_id")
                else app.begin(identity)
            )
            if not app.sessions.is_active(identity, turn):
                return handler.reply(
                    409, {"error": "Search cancelled; start a new turn."}
                )
            result = adapter.search(
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
            if not app.sessions.is_active(identity, turn):
                return handler.reply(
                    409, {"error": "Search cancelled; no result was published."}
                )
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
            turn = uuid_text(body["turn_id"])
            return handler.reply(
                200,
                asdict(
                    app.final(
                        identity, Transcript(TranscriptKind.FINAL, body["text"], turn)
                    )
                ),
            )
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
                        "SELECT operation_id,status,created_at FROM commands WHERE session_id=%s UNION ALL SELECT operation_id,'committed',committed_at AS created_at FROM cart_adjustments WHERE session_id=%s ORDER BY created_at DESC LIMIT 10",
                        (identity, identity),
                    )
                )
            return handler.reply(200, {"operations": rows})
        if resource == "cart" and method == "GET":
            return handler.reply(200, adapter.cart(identity))
        if resource == "cart/add" and method == "POST":
            body = handler.body()
            operation = uuid_text(body["operation_id"])
            body["unit_price_minor"] = minor_units(body["unit_price_minor"])
            quantity = body.get("quantity", 1)
            if type(quantity) is not int or not 1 <= quantity <= 99:
                raise ValueError("Quantity 1–99 required")
            from voicecart.merchant import AddIntent

            intent = AddIntent(
                operation,
                body["variant_id"],
                quantity,
                body["currency"],
                body["revision"],
                body["unit_price_minor"],
            )
            receipt = adapter.add(identity, intent)
            response = app.confirmed_receipt(identity, receipt.turn_id, receipt)
            return handler.reply(200, asdict(response))
        if resource == "cart/quantity" and method == "POST":
            body = handler.body()
            operation = body["operation_id"]
            receipt = adapter.set_quantity(
                identity,
                operation,
                body["variant_id"],
                body["quantity"],
                body["currency"],
            )
            return handler.reply(200, receipt)
        if resource == "cart/retry" and method == "POST":
            operation = handler.body()["operation_id"]
            receipt = adapter.management.receipt(identity, operation)
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
            turn = app.begin(identity)
            cancellation = app.cancellation_event(identity, turn)
            with web.speech_lock:
                recognizer = web.recognizers.setdefault(tenant, None)
                if recognizer is None:
                    recognizer = WhisperRecognizer(settings.asr)
                    web.recognizers[tenant] = recognizer
            transcript = recognizer.transcribe(pcm, turn, cancelled=cancellation)
            if cancellation.is_set() or not app.sessions.is_active(identity, turn):
                return handler.reply(
                    409, {"error": "Transcription cancelled. No cart action was sent."}
                )
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
    if parts[2] == "merchant":
        from voicecart.merchant_api import merchant

        merchant(handler, tenant, "/".join(parts[3:]))
    elif parts[2] == "admin":
        from voicecart.admin import admin

        admin(handler, tenant, "/".join(parts[3:]))
    else:
        customer(handler, tenant, "/".join(parts[2:]))
    return True
