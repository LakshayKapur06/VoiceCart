"""Session-scoped local cart transactions, immutable receipts and retry identity.

This is neither a merchant cart nor a reservation/order/payment system.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import weakref
from dataclasses import asdict, dataclass, replace
from datetime import datetime

import psycopg
from psycopg.types.json import Jsonb

from voicecart.catalogue import qualify
from voicecart.database import Database, DatabaseUnavailable
from voicecart.domain import (
    Eligibility,
    ExactIdentifier,
    HardConstraints,
    IdentifierKind,
    Money,
    PriceLimit,
    PriceOperator,
    RetrievalRoute,
    SearchRequest,
    require_integer,
    require_text,
)
from voicecart.sessions import SessionError, SessionStore, uuid_text


class CartError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class OutcomeUnknown(CartError):
    def __init__(self):
        super().__init__("outcome_unknown_retry_same_operation")


@dataclass(frozen=True)
class AddCommand:
    session_id: str
    turn_id: str
    operation_id: str
    selection: str
    request: SearchRequest
    variant_id: str | None = None
    expected_revision: str | None = None
    expected_unit_price_minor: int | None = None

    def __post_init__(self):
        for value in (self.session_id, self.turn_id, self.operation_id):
            uuid_text(value)
        if (
            not isinstance(self.request, SearchRequest)
            or self.request.route is RetrievalRoute.DISCOVERY
        ):
            raise CartError("unverified_discovery_cannot_authorize_query_add")
        if self.selection == "exact":
            require_text(self.variant_id, "variant_id")
        elif self.selection == "cheapest":
            if (
                self.variant_id is not None
                or self.request.route is not RetrievalRoute.STRUCTURED
            ):
                raise CartError("invalid_cheapest_command")
        else:
            raise CartError("unsupported_selection")
        if self.expected_unit_price_minor is not None:
            require_integer(self.expected_unit_price_minor, "expected_unit_price_minor")

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()


def decode_command(payload: dict) -> AddCommand:
    fields = dict(payload)
    request = fields["request"]
    constraints = dict(request["constraints"])
    if constraints["price_limit"] is not None:
        limit = constraints["price_limit"]
        constraints["price_limit"] = PriceLimit(
            Money(**limit["amount"]), PriceOperator(limit["operator"])
        )
    identifier = request["identifier"]
    fields["request"] = SearchRequest(
        HardConstraints(**constraints),
        RetrievalRoute(request["route"]),
        ExactIdentifier(IdentifierKind(identifier["kind"]), identifier["value"])
        if identifier
        else None,
        request["semantic_query"],
    )
    return AddCommand(**fields)


@dataclass(frozen=True)
class Receipt:
    operation_id: str
    session_id: str
    turn_id: str
    fingerprint: str
    variant_id: str
    product_name: str
    added_quantity: int
    resulting_quantity: int
    unit_price_minor: int
    line_price_minor: int
    currency: str
    catalogue_revision: str
    committed_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> Receipt:
        fields = dict(row)
        for name in ("operation_id", "session_id", "turn_id"):
            fields[name] = str(fields[name])
        return cls(**fields)


class CartService:
    def __init__(self, database: Database):
        self.database = database
        self.sessions = SessionStore(database)
        self._locks: weakref.WeakValueDictionary[str, threading.Lock] = (
            weakref.WeakValueDictionary()
        )
        self._guard = threading.Lock()

    def _lock(self, session_id: str):
        with self._guard:
            return self._locks.setdefault(session_id, threading.Lock())

    def prepare(self, command: AddCommand) -> None:
        with self.database.connect() as connection:
            session = self.sessions.require(connection, command.session_id, lock=True)
            existing = connection.execute(
                "SELECT * FROM commands WHERE operation_id=%s", (command.operation_id,)
            ).fetchone()
            if existing:
                if (
                    str(existing["session_id"]) != command.session_id
                    or existing["fingerprint"] != command.fingerprint
                ):
                    raise CartError("operation_identity_conflict")
                return
            if str(session["active_turn"]) != command.turn_id:
                raise CartError("turn_cancelled_or_superseded")
            pending = connection.execute(
                "SELECT operation_id FROM commands WHERE session_id=%s AND status='prepared'",
                (command.session_id,),
            ).fetchone()
            if pending:
                raise CartError("resolve_previous_operation_first")
            connection.execute(
                "INSERT INTO commands(operation_id,session_id,turn_id,fingerprint,payload,status) VALUES (%s,%s,%s,%s,%s,'prepared')",
                (
                    command.operation_id,
                    command.session_id,
                    command.turn_id,
                    command.fingerprint,
                    Jsonb(asdict(command)),
                ),
            )

    def read_receipt(self, session_id: str, operation_id: str) -> Receipt | None:
        uuid_text(operation_id)
        with self.database.connect() as connection:
            self.sessions.require(connection, session_id)
            row = connection.execute(
                "SELECT * FROM operation_receipts WHERE operation_id=%s AND session_id=%s",
                (operation_id, session_id),
            ).fetchone()
            return Receipt.from_row(row) if row else None

    def load_command(self, session_id: str, operation_id: str) -> AddCommand:
        uuid_text(operation_id)
        with self.database.connect() as connection:
            self.sessions.require(connection, session_id)
            row = connection.execute(
                "SELECT payload FROM commands WHERE operation_id=%s AND session_id=%s",
                (operation_id, session_id),
            ).fetchone()
            if row is None:
                raise CartError("unknown_operation")
            return decode_command(row["payload"])

    def pending(self, session_id: str) -> str | None:
        with self.database.connect() as connection:
            self.sessions.require(connection, session_id)
            row = connection.execute(
                "SELECT operation_id FROM commands WHERE session_id=%s AND status='prepared'",
                (session_id,),
            ).fetchone()
            return str(row["operation_id"]) if row else None

    def _execute_once(
        self, command: AddCommand, cancelled: threading.Event | None
    ) -> Receipt:
        with self.database.connect() as connection:
            connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            session = self.sessions.require(connection, command.session_id, lock=True)
            record = connection.execute(
                "SELECT * FROM commands WHERE operation_id=%s", (command.operation_id,)
            ).fetchone()
            if (
                record is None
                or record["fingerprint"] != command.fingerprint
                or str(record["session_id"]) != command.session_id
            ):
                raise CartError("operation_identity_conflict")
            row = connection.execute(
                "SELECT * FROM operation_receipts WHERE operation_id=%s",
                (command.operation_id,),
            ).fetchone()
            if row:
                return Receipt.from_row(
                    row
                )  # Before any fresh selection or stale-turn checks.
            if record["status"] != "prepared":
                raise CartError(record["failure_code"] or "operation_not_pending")
            if str(session["active_turn"]) != command.turn_id or (
                cancelled is not None and cancelled.is_set()
            ):
                raise CartError("turn_cancelled_or_superseded")
            connection.execute(
                "SELECT singleton FROM catalogue_state WHERE singleton=true FOR SHARE"
            )
            snapshot = self.database.snapshot_in(connection)
            constraints = command.request.constraints
            cart = {
                row["variant_id"]: row["quantity"]
                for row in connection.execute(
                    "SELECT variant_id,quantity FROM cart_items WHERE session_id=%s",
                    (command.session_id,),
                )
            }
            if command.selection == "cheapest":
                result = snapshot.catalogue.search(command.request)
                if not result.can_claim_catalogue_minimum:
                    raise CartError("complete_current_minimum_not_verified")
                eligible = []
                for item in result.matches:
                    aggregate = (
                        cart.get(item.variant.variant_id, 0) + constraints.quantity
                    )
                    require_integer(aggregate, "aggregate_quantity", 1)
                    assessment = qualify(item, replace(constraints, quantity=aggregate))
                    if assessment.state is Eligibility.UNKNOWN:
                        raise CartError("aggregate_eligibility_unknown")
                    if assessment.state is Eligibility.QUALIFIED:
                        eligible.append(item)

                def key(item):
                    return item.variant.price.minor_units, item.variant.variant_id

                selected = min(eligible, key=key, default=None)
                if selected is None:
                    raise CartError("no_eligible_stock_for_cart")
            else:
                items = snapshot.catalogue.lookup(
                    ExactIdentifier(IdentifierKind.VARIANT_ID, command.variant_id or "")
                )
                if len(items) != 1:
                    raise CartError("selected_variant_unavailable")
                selected = items[0]
            identifier = selected.variant.variant_id
            connection.execute(
                "SELECT variant_id FROM variants WHERE variant_id=%s FOR UPDATE",
                (identifier,),
            ).fetchone()
            aggregate = cart.get(identifier, 0) + constraints.quantity
            require_integer(aggregate, "aggregate_quantity", 1)
            if (
                qualify(selected, replace(constraints, quantity=aggregate)).state
                is not Eligibility.QUALIFIED
            ):
                raise CartError("current_price_stock_or_attributes_not_eligible")
            price = selected.variant.price
            if price is None:
                raise CartError("current_price_not_verified")
            if (
                command.expected_revision is not None
                and command.expected_revision != snapshot.state["revision"]
            ) or (
                command.expected_unit_price_minor is not None
                and command.expected_unit_price_minor != price.minor_units
            ):
                raise CartError("offer_changed_search_or_confirm_again")
            line_price = price.minor_units * constraints.quantity
            require_integer(line_price, "line_price_minor")
            if cancelled is not None and cancelled.is_set():
                raise CartError("turn_cancelled_or_superseded")
            connection.execute(
                "INSERT INTO cart_items(session_id,variant_id,quantity) VALUES (%s,%s,%s) ON CONFLICT(session_id,variant_id) DO UPDATE SET quantity=excluded.quantity",
                (command.session_id, identifier, aggregate),
            )
            connection.execute(
                "UPDATE sessions SET mutation_version=mutation_version+1 WHERE session_id=%s",
                (command.session_id,),
            )
            row = connection.execute(
                "INSERT INTO operation_receipts(operation_id,session_id,turn_id,fingerprint,variant_id,product_name,added_quantity,resulting_quantity,unit_price_minor,line_price_minor,currency,catalogue_revision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    command.operation_id,
                    command.session_id,
                    command.turn_id,
                    command.fingerprint,
                    identifier,
                    selected.product.name,
                    constraints.quantity,
                    aggregate,
                    price.minor_units,
                    line_price,
                    price.currency,
                    snapshot.state["revision"],
                ),
            ).fetchone()
            connection.execute(
                "UPDATE commands SET status='committed' WHERE operation_id=%s",
                (command.operation_id,),
            )
            receipt = Receipt.from_row(row)
        return receipt  # The transaction has committed; verification uses a new connection.

    def _reject(self, command: AddCommand, code: str) -> None:
        try:
            with self.database.connect() as connection:
                self.sessions.require(connection, command.session_id, lock=True)
                connection.execute(
                    "UPDATE commands SET status='rejected',failure_code=%s WHERE operation_id=%s AND session_id=%s AND fingerprint=%s AND status='prepared'",
                    (
                        code,
                        command.operation_id,
                        command.session_id,
                        command.fingerprint,
                    ),
                )
        except (DatabaseUnavailable, SessionError):
            pass  # Leave prepared identity for explicit recovery; never allocate a replacement.

    def add(
        self, command: AddCommand, *, cancelled: threading.Event | None = None
    ) -> Receipt:
        lock = self._lock(command.session_id)
        if not lock.acquire(timeout=5):
            raise CartError("session_busy_retry_same_operation")
        try:
            for attempt in range(3):
                try:
                    self.prepare(command)
                    self._execute_once(command, cancelled)
                    verified = self.read_receipt(
                        command.session_id, command.operation_id
                    )
                    if verified is None or verified.fingerprint != command.fingerprint:
                        raise OutcomeUnknown()
                    return verified
                except (
                    psycopg.errors.SerializationFailure,
                    psycopg.errors.DeadlockDetected,
                    psycopg.errors.LockNotAvailable,
                ):
                    if attempt == 2:
                        raise CartError(
                            "transaction_busy_retry_same_operation"
                        ) from None
                    time.sleep(0.01 * (attempt + 1))
                except DatabaseUnavailable:
                    try:
                        receipt = self.read_receipt(
                            command.session_id, command.operation_id
                        )
                    except DatabaseUnavailable:
                        receipt = None
                    if (
                        receipt is not None
                        and receipt.fingerprint == command.fingerprint
                    ):
                        return receipt
                    raise OutcomeUnknown() from None
                except psycopg.errors.UniqueViolation:
                    raise CartError("operation_identity_conflict") from None
                except OutcomeUnknown:
                    raise
                except CartError as exc:
                    self._reject(command, exc.code)
                    raise
                except (TypeError, ValueError) as exc:
                    self._reject(command, "invalid_or_expired_operation")
                    raise CartError("invalid_or_expired_operation") from exc
            raise CartError("transaction_retry_limit")
        finally:
            lock.release()

    def retry(self, session_id: str, operation_id: str) -> Receipt:
        return self.add(self.load_command(session_id, operation_id))

    def items(self, session_id: str) -> dict[str, int]:
        with self.database.connect() as connection:
            self.sessions.require(connection, session_id)
            return {
                row["variant_id"]: row["quantity"]
                for row in connection.execute(
                    "SELECT variant_id,quantity FROM cart_items WHERE session_id=%s ORDER BY variant_id",
                    (session_id,),
                )
            }
