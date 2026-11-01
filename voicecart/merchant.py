"""Shared merchant contract and the implemented authoritative local-store adapter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from voicecart.browse import CatalogueBrowser
from voicecart.cart import AddCommand, CartError, Receipt
from voicecart.cart_management import CartManagement
from voicecart.domain import (
    ExactIdentifier,
    HardConstraints,
    IdentifierKind,
    RetrievalRoute,
    SearchRequest,
)
from voicecart.ingestion import CatalogueImport
from voicecart.sessions import uuid_text


@dataclass(frozen=True)
class AddIntent:
    operation_id: str
    variant_id: str
    quantity: int
    currency: str
    revision: str
    unit_price_minor: int


class MerchantAdapter(Protocol):
    """An external implementation must revalidate in its own system of record."""

    def search(self, query: str = "", **filters) -> dict: ...
    def lookup(self, product_id: str) -> dict: ...
    def synchronize(self, snapshot: CatalogueImport) -> str: ...
    def refresh_offers(self, variant_ids: list[str]) -> list[dict]: ...
    def add(self, session_id: str, intent: AddIntent) -> Receipt: ...
    def set_quantity(
        self,
        session_id: str,
        operation_id: str,
        variant_id: str,
        quantity: int,
        currency: str,
    ) -> dict: ...
    def cart(self, session_id: str) -> dict: ...
    def operation(self, session_id: str, operation_id: str) -> dict: ...


class LocalMerchantAdapter:
    """PostgreSQL is truth for this local cart only, not for an outside merchant."""

    def __init__(self, application):
        self.application = application
        self.database = application.database
        self.management = CartManagement(self.database)

    def search(self, query="", **filters):
        return CatalogueBrowser(
            self.database, self.application.catalogue.encoder
        ).search(query, **filters)

    def lookup(self, product_id):
        if not isinstance(product_id, str) or not 1 <= len(product_id) <= 256:
            raise ValueError("Invalid product identifier")
        with self.database.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            snapshot = self.database.snapshot_in(connection)
            items = [
                item for item in snapshot.items if item.product.product_id == product_id
            ]
            if not items:
                raise ValueError("Unknown product")
            row = connection.execute(
                "SELECT payload FROM product_metadata WHERE product_id=%s",
                (product_id,),
            ).fetchone()
        return {
            "product": asdict(items[0].product),
            "variants": [asdict(item.variant) for item in items],
            "metadata": row["payload"] if row else {},
            "revision": snapshot.state["revision"],
            "authority": "local PostgreSQL source; historical metadata is not current inventory",
        }

    def synchronize(self, snapshot):
        return self.database.publish(
            snapshot, encoder=self.application.catalogue.encoder
        )

    def refresh_offers(self, variant_ids):
        if (
            not isinstance(variant_ids, list)
            or not 1 <= len(variant_ids) <= 100
            or any(
                not isinstance(value, str) or len(value) > 256 for value in variant_ids
            )
        ):
            raise ValueError("Bounded variant IDs required")
        snapshot = self.database.snapshot()
        by_id = {item.variant.variant_id: item.variant for item in snapshot.items}
        return [
            {
                "variant_id": value,
                "offer": asdict(by_id[value]) if value in by_id else None,
                "revision": snapshot.state["revision"],
                "refresh_source": "local current database snapshot; no upstream Amazon request",
            }
            for value in variant_ids
        ]

    def add(self, session_id, intent):
        uuid_text(intent.operation_id)
        if type(intent.quantity) is not int or not 1 <= intent.quantity <= 99:
            raise ValueError("Quantity 1–99 required")
        app = self.application
        try:
            command = app.cart.load_command(session_id, intent.operation_id)
            if (
                command.variant_id,
                command.request.constraints.currency,
                command.request.constraints.quantity,
                command.expected_revision,
                command.expected_unit_price_minor,
            ) != (
                intent.variant_id,
                intent.currency,
                intent.quantity,
                intent.revision,
                intent.unit_price_minor,
            ):
                raise CartError("operation_identity_conflict")
        except CartError as error:
            if error.code != "unknown_operation":
                raise
            turn = app.begin(session_id)
            request = SearchRequest(
                HardConstraints(intent.currency, quantity=intent.quantity),
                RetrievalRoute.EXACT,
                ExactIdentifier(IdentifierKind.VARIANT_ID, intent.variant_id),
            )
            command = AddCommand(
                session_id,
                turn,
                intent.operation_id,
                "exact",
                request,
                intent.variant_id,
                intent.revision,
                intent.unit_price_minor,
            )
            app.cart.prepare(command)
        return app.cart.add(command)

    def set_quantity(self, session_id, operation_id, variant_id, quantity, currency):
        return self.management.set_quantity(
            session_id, operation_id, variant_id, quantity, currency
        )

    def cart(self, session_id):
        return self.management.overview(session_id)

    def operation(self, session_id, operation_id):
        receipt = self.management.receipt(session_id, operation_id)
        if receipt:
            return receipt
        stored = self.application.cart.read_receipt(session_id, operation_id)
        if stored:
            return {"status": "committed", "receipt": asdict(stored)}
        try:
            command = self.application.cart.load_command(session_id, operation_id)
        except CartError:
            return {"status": "unknown", "operation_id": operation_id}
        with self.database.connect() as connection:
            status = connection.execute(
                "SELECT status FROM commands WHERE operation_id=%s",
                (command.operation_id,),
            ).fetchone()["status"]
        return {
            "status": status,
            "operation_id": operation_id,
            "recovery": "Retry the identical authorized request and original operation ID; never invent a replacement.",
        }
