"""Expiring local session and presented-result identity, owned by the application."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta

from psycopg.types.json import Jsonb

from voicecart.database import Database
from voicecart.domain import SearchResult, require_integer


class SessionError(ValueError):
    pass


def uuid_text(value: str) -> str:
    try:
        if not isinstance(value, str) or str(uuid.UUID(value)) != value:
            raise ValueError("A canonical UUID is required")
    except (ValueError, AttributeError) as exc:
        raise SessionError("Invalid session, turn or operation identity") from exc
    return value


@dataclass(frozen=True)
class Offer:
    variant_id: str
    product_name: str
    unit_price_minor: int
    currency: str
    catalogue_revision: str
    colour: str | None
    size: str | None
    cheapest: bool = False


@dataclass(frozen=True)
class ResultList:
    list_id: str
    turn_id: str
    offers: tuple[Offer, ...]


class SessionStore:
    def __init__(self, database: Database):
        self.database = database

    def create(self, *, ttl_seconds: int = 3600) -> str:
        require_integer(ttl_seconds, "ttl_seconds", 60)
        if ttl_seconds > 86400:
            raise SessionError("Session lifetime is at most one day")
        identifier = str(uuid.uuid4())
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO sessions(session_id,expires_at) VALUES (%s,%s)",
                (identifier, datetime.now(UTC) + timedelta(seconds=ttl_seconds)),
            )
        return identifier

    def require(self, connection, session_id: str, *, lock: bool = False) -> dict:
        uuid_text(session_id)
        query = (
            "SELECT * FROM sessions WHERE session_id=%s FOR UPDATE"
            if lock
            else "SELECT * FROM sessions WHERE session_id=%s"
        )
        row = connection.execute(query, (session_id,)).fetchone()
        if row is None or row["expires_at"] <= datetime.now(UTC):
            raise SessionError(
                "Session expired. Start a new session; old actions are not replayed."
            )
        return dict(row)

    def begin_turn(self, session_id: str) -> str:
        turn_id = str(uuid.uuid4())
        with self.database.connect() as connection:
            self.require(connection, session_id, lock=True)
            connection.execute(
                "UPDATE sessions SET active_turn=%s,accepted_turn=NULL WHERE session_id=%s",
                (turn_id, session_id),
            )
        return turn_id

    def claim_final(self, session_id: str, turn_id: str) -> bool:
        uuid_text(turn_id)
        with self.database.connect() as connection:
            session = self.require(connection, session_id, lock=True)
            if (
                str(session["active_turn"]) != turn_id
                or str(session["accepted_turn"]) == turn_id
            ):
                return False
            connection.execute(
                "UPDATE sessions SET accepted_turn=%s WHERE session_id=%s",
                (turn_id, session_id),
            )
            return True

    def is_active(self, session_id: str, turn_id: str) -> bool:
        uuid_text(turn_id)
        with self.database.connect() as connection:
            session = self.require(connection, session_id)
            return str(session["active_turn"]) == turn_id

    def invalidate_results(self, session_id: str, turn_id: str) -> None:
        with self.database.connect() as connection:
            row = self.require(connection, session_id, lock=True)
            if str(row["active_turn"]) == turn_id:
                connection.execute(
                    "UPDATE sessions SET current_list_id=NULL WHERE session_id=%s",
                    (session_id,),
                )

    def publish_results(
        self, session_id: str, turn_id: str, result: SearchResult
    ) -> ResultList | None:
        uuid_text(turn_id)
        ordered = list((result.ranked_matches or result.matches)[:3])
        cheapest = result.cheapest_qualifying_match
        if cheapest is not None and all(
            item.variant.variant_id != cheapest.variant.variant_id for item in ordered
        ):
            ordered.append(cheapest)
        offers = []
        for item in ordered:
            price = item.variant.price
            if price is None:
                raise SessionError("Cannot present an unverified price")
            offers.append(
                Offer(
                    item.variant.variant_id,
                    item.product.name,
                    price.minor_units,
                    price.currency,
                    result.catalogue_revision,
                    item.variant.colour,
                    item.variant.size,
                    cheapest is not None
                    and item.variant.variant_id == cheapest.variant.variant_id,
                )
            )
        with self.database.connect() as connection:
            session = self.require(connection, session_id, lock=True)
            if str(session["active_turn"]) != turn_id:
                raise SessionError("Search result belongs to an expired turn")
            if not offers:
                connection.execute(
                    "UPDATE sessions SET current_list_id=NULL WHERE session_id=%s",
                    (session_id,),
                )
                return None
            identifier = str(uuid.uuid4())
            expires = min(
                session["expires_at"], datetime.now(UTC) + timedelta(minutes=5)
            )
            connection.execute(
                "INSERT INTO result_lists(list_id,session_id,turn_id,catalogue_revision,offers,expires_at) VALUES (%s,%s,%s,%s,%s,%s)",
                (
                    identifier,
                    session_id,
                    turn_id,
                    result.catalogue_revision,
                    Jsonb([asdict(offer) for offer in offers]),
                    expires,
                ),
            )
            connection.execute(
                "UPDATE sessions SET current_list_id=%s WHERE session_id=%s",
                (identifier, session_id),
            )
        return ResultList(identifier, turn_id, tuple(offers))

    def mark_presented(self, session_id: str, list_id: str, turn_id: str) -> bool:
        uuid_text(list_id)
        uuid_text(turn_id)
        with self.database.connect() as connection:
            session = self.require(connection, session_id, lock=True)
            if (
                str(session["active_turn"]) != turn_id
                or str(session["current_list_id"]) != list_id
            ):
                return False
            row = connection.execute(
                "UPDATE result_lists SET presented=true WHERE list_id=%s AND session_id=%s AND expires_at>now() RETURNING list_id",
                (list_id, session_id),
            ).fetchone()
            return row is not None

    def resolve(
        self, session_id: str, ordinal: int, *, list_id: str | None = None
    ) -> Offer:
        require_integer(ordinal, "ordinal", 1)
        with self.database.connect() as connection:
            session = self.require(connection, session_id)
            current = (
                str(session["current_list_id"]) if session["current_list_id"] else None
            )
            if current is None or (list_id is not None and list_id != current):
                raise SessionError(
                    "That result list is no longer current. Search again."
                )
            row = connection.execute(
                "SELECT * FROM result_lists WHERE list_id=%s AND session_id=%s",
                (current, session_id),
            ).fetchone()
            if (
                row is None
                or not row["presented"]
                or row["expires_at"] <= datetime.now(UTC)
            ):
                raise SessionError(
                    "Read or replay the complete current result list before selecting an item."
                )
            if ordinal > len(row["offers"]):
                raise SessionError("That result number is not in the current list.")
            return Offer(**row["offers"][ordinal - 1])

    def cancel(self, session_id: str) -> None:
        with self.database.connect() as connection:
            self.require(connection, session_id, lock=True)
            connection.execute(
                "UPDATE commands SET status='cancelled',failure_code='cancelled' WHERE session_id=%s AND status='prepared'",
                (session_id,),
            )
            connection.execute(
                "UPDATE sessions SET active_turn=NULL,current_list_id=NULL WHERE session_id=%s",
                (session_id,),
            )

    def cleanup_expired(self) -> int:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM sessions WHERE expires_at<=now()")
            return cursor.rowcount
