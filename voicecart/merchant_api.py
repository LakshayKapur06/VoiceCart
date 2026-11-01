"""Merchant-server API using the same adapter as the local customer workflow."""

from dataclasses import asdict

from voicecart.admin import authorized
from voicecart.cart import CartError, OutcomeUnknown
from voicecart.merchant import AddIntent
from voicecart.sessions import SessionError
from voicecart.web_api import minor_units


def merchant(handler, tenant, resource):
    authorized(handler, tenant)
    if handler.command != "POST":
        return handler.reply(405, {"error": "POST required"})
    body = handler.body()
    app = handler.server.application.apps[tenant]
    adapter = handler.server.application.adapters[tenant]
    try:
        if resource == "sessions":
            return handler.reply(
                201, {"session_id": app.sessions.create(), "merchant": tenant}
            )
        if resource == "lookup":
            return handler.reply(200, adapter.lookup(body["product_id"]))
        if resource == "refresh":
            return handler.reply(
                200, {"offers": adapter.refresh_offers(body["variant_ids"])}
            )
        if resource == "search":
            return handler.reply(
                200,
                adapter.search(
                    body.get("query", ""),
                    currency=body.get("currency"),
                    category=body.get("category", ""),
                    brand=body.get("brand", ""),
                    offset=body.get("offset", 0),
                    limit=body.get("limit", 24),
                ),
            )
        if resource == "cart":
            return handler.reply(200, adapter.cart(body["session_id"]))
        if resource == "add":
            intent = AddIntent(
                body["operation_id"],
                body["variant_id"],
                body.get("quantity", 1),
                body["currency"],
                body["revision"],
                minor_units(body["unit_price_minor"]),
            )
            return handler.reply(
                200,
                {
                    "status": "committed",
                    "receipt": asdict(adapter.add(body["session_id"], intent)),
                },
            )
        if resource == "quantity":
            return handler.reply(
                200,
                adapter.set_quantity(
                    body["session_id"],
                    body["operation_id"],
                    body["variant_id"],
                    body["quantity"],
                    body["currency"],
                ),
            )
        if resource == "operation":
            return handler.reply(
                200, adapter.operation(body["session_id"], body["operation_id"])
            )
    except OutcomeUnknown:
        return handler.reply(
            409,
            {
                "error": "Outcome unknown; retain operation ID and reconcile",
                "operation_id": body.get("operation_id"),
            },
        )
    except (CartError, SessionError):
        return handler.reply(
            409,
            {"error": "Operation/session/offer rejected; no new mutation confirmed"},
        )
    return handler.reply(404, {"error": "Unknown merchant operation"})
