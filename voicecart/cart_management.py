"""Target-quantity/removal transactions with immutable idempotent receipts."""

from __future__ import annotations

import hashlib
import json

import psycopg
from psycopg.types.json import Jsonb

from voicecart.cart import CartError, OutcomeUnknown
from voicecart.catalogue import qualify
from voicecart.database import DatabaseUnavailable
from voicecart.domain import (
    Eligibility,
    HardConstraints,
    require_currency,
    require_integer,
    require_text,
)
from voicecart.sessions import SessionStore, uuid_text


class CartManagement:
    def __init__(self, database):
        self.database = database
        self.sessions = SessionStore(database)

    def receipt(self, session, operation):
        uuid_text(operation)
        with self.database.connect() as connection:
            self.sessions.require(connection, session)
            row = connection.execute(
                "SELECT receipt FROM cart_adjustments WHERE operation_id=%s AND session_id=%s",
                (operation, session),
            ).fetchone()
            return row["receipt"] if row else None

    def set_quantity(self, session, operation, variant, quantity, currency):
        uuid_text(operation)
        require_text(variant, "variant")
        require_integer(quantity, "quantity")
        require_currency(currency)
        if quantity > 99:
            raise CartError("quantity_above_99")
        fingerprint = hashlib.sha256(
            json.dumps(
                [session, variant, quantity, currency], separators=(",", ":")
            ).encode()
        ).hexdigest()
        try:
            with self.database.connect() as connection:
                self.sessions.require(connection, session, lock=True)
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (operation,)
                )
                old = connection.execute(
                    "SELECT fingerprint,receipt FROM cart_adjustments WHERE operation_id=%s",
                    (operation,),
                ).fetchone()
                if old:
                    if old["fingerprint"] != fingerprint:
                        raise CartError("operation_identity_conflict")
                    return old["receipt"]
                if connection.execute(
                    "SELECT 1 FROM commands WHERE operation_id=%s", (operation,)
                ).fetchone():
                    raise CartError("operation_identity_conflict")
                current = connection.execute(
                    "SELECT quantity FROM cart_items WHERE session_id=%s AND variant_id=%s FOR UPDATE",
                    (session, variant),
                ).fetchone()
                if not current:
                    raise CartError("cart_line_not_found")
                if quantity > current["quantity"]:
                    connection.execute(
                        "LOCK TABLE catalogue_state,products,variants IN SHARE MODE"
                    )
                    snapshot = self.database.snapshot_in(connection)
                    item = next(
                        (
                            row
                            for row in snapshot.items
                            if row.variant.variant_id == variant
                        ),
                        None,
                    )
                    if (
                        item is None
                        or qualify(
                            item, HardConstraints(currency, quantity=quantity)
                        ).state
                        is not Eligibility.QUALIFIED
                        or item.variant.stock_quantity is None
                    ):
                        raise CartError("current_quantity_not_eligible")
                if quantity == 0:
                    connection.execute(
                        "DELETE FROM cart_items WHERE session_id=%s AND variant_id=%s",
                        (session, variant),
                    )
                else:
                    connection.execute(
                        "UPDATE cart_items SET quantity=%s WHERE session_id=%s AND variant_id=%s",
                        (quantity, session, variant),
                    )
                receipt = {
                    "operation_id": operation,
                    "variant_id": variant,
                    "quantity": quantity,
                    "status": "committed",
                    "kind": "set_quantity",
                }
                connection.execute(
                    "INSERT INTO cart_adjustments(operation_id,session_id,fingerprint,receipt) VALUES (%s,%s,%s,%s)",
                    (operation, session, fingerprint, Jsonb(receipt)),
                )
        except (DatabaseUnavailable, psycopg.OperationalError):
            try:
                receipt = self.receipt(session, operation)
            except (DatabaseUnavailable, psycopg.Error):
                receipt = None
            if receipt:
                return receipt
            raise OutcomeUnknown() from None
        receipt = self.receipt(session, operation)
        if receipt is None:
            raise OutcomeUnknown()
        return receipt

    def overview(self, session):
        with self.database.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            self.sessions.require(connection, session)
            snapshot = self.database.snapshot_in(connection)
            lines = list(
                connection.execute(
                    "SELECT variant_id,quantity FROM cart_items WHERE session_id=%s ORDER BY variant_id",
                    (session,),
                )
            )
        by_id = {item.variant.variant_id: item for item in snapshot.items}
        subtotals: dict[str, int] = {}
        result = []
        unknown = 0
        for row in lines:
            item = by_id.get(row["variant_id"])
            price = (
                item.variant.price
                if item and item.variant.price_freshness.value == "current"
                else None
            )
            if price:
                total = price.minor_units * row["quantity"]
                subtotals[price.currency] = subtotals.get(price.currency, 0) + total
            else:
                unknown += 1
            result.append(
                {
                    **dict(row),
                    "name": item.product.name if item else "Unavailable product",
                    "currency": price.currency if price else None,
                    "unit_price_minor": price.minor_units if price else None,
                    "line_total_minor": price.minor_units * row["quantity"]
                    if price
                    else None,
                }
            )
        return {
            "items": result,
            "subtotals_minor": subtotals,
            "unpriced_lines": unknown,
            "totals_complete": unknown == 0,
            "scope": "Current verified prices, grouped by currency. No checkout or stock reservation.",
        }
