"""Deterministic search/clarify/select/add orchestration; models never own actions."""

from __future__ import annotations

import re
import threading
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Protocol

import psycopg

from voicecart.audio import Transcript, TranscriptKind
from voicecart.cart import AddCommand, CartError, CartService, OutcomeUnknown, Receipt
from voicecart.database import Database, DatabaseUnavailable
from voicecart.domain import (
    HardConstraints,
    RetrievalRoute,
    SearchRequest,
    SearchStatus,
)
from voicecart.local_http import LocalServiceError
from voicecart.nlu import Intent, InterpretationError
from voicecart.search import PostgresCatalogue
from voicecart.sessions import ResultList, SessionError, SessionStore


def display_text(value: str, limit: int = 180) -> str:
    # Catalogue/user text must not inject terminal controls or fake status lines.
    return re.sub(
        r"\s+",
        " ",
        "".join(character for character in value if character.isprintable()),
    ).strip()[:limit]


def money_text(amount: int, currency: str) -> str:
    if currency == "INR":
        rupees, paise = divmod(amount, 100)
        return f"{rupees} rupees" + (f" and {paise} paise" if paise else "")
    return f"{amount} minor units {currency}"


class Interpreter(Protocol):
    def interpret(
        self, transcript: str, vocabulary: dict[str, dict[str, str]]
    ) -> Intent: ...


@dataclass(frozen=True)
class Response:
    code: str
    text: str
    session_id: str
    turn_id: str
    listing: ResultList | None = None
    operation_id: str | None = None
    receipt: Receipt | None = None


class ShoppingApplication:
    def __init__(
        self,
        database: Database,
        interpreter: Interpreter | None,
        catalogue: PostgresCatalogue | None = None,
    ):
        self.database = database
        self.interpreter = interpreter
        self.catalogue = catalogue or PostgresCatalogue(database)
        self.sessions = SessionStore(database)
        self.cart = CartService(database)
        self._last: dict[str, Response] = {}
        self._events: dict[str, threading.Event] = {}
        self._turns: dict[str, str] = {}
        self._guard = threading.RLock()

    def begin(self, session_id: str) -> str:
        with self._guard:
            previous = self._events.get(session_id)
            if previous:
                previous.set()
            turn = self.sessions.begin_turn(session_id)
            self._events[session_id] = threading.Event()
            self._turns[session_id] = turn
            return turn

    def remember(self, response: Response) -> Response:
        with self._guard:
            if (
                response.text
                and response.code not in ("cancelled", "busy", "partial")
                and (
                    not response.turn_id
                    or self._turns.get(response.session_id) == response.turn_id
                )
            ):
                self._last[response.session_id] = response
        return response

    def cancellation_event(self, session_id: str, turn_id: str) -> threading.Event:
        with self._guard:
            if self._turns.get(session_id) == turn_id:
                return self._events[session_id]
        event = threading.Event()
        event.set()
        return event

    def error(self, session_id: str, turn_id: str, code: str, text: str) -> Response:
        with self._guard:
            if turn_id and self._turns.get(session_id) != turn_id:
                return Response("cancelled", "", session_id, turn_id)
        return self.remember(Response(code, text, session_id, turn_id))

    def repeat(self, session_id: str) -> Response:
        with self._guard:
            previous = self._last.get(session_id)
        if previous is None:
            return Response(
                "nothing_to_repeat",
                "There is no response to repeat yet.",
                session_id,
                "",
            )
        return previous  # No inference, search or cart dispatch.

    def cancel(self, session_id: str) -> Response:
        with self._guard:
            if event := self._events.get(session_id):
                event.set()
            self._turns.pop(session_id, None)
        self.sessions.cancel(session_id)
        return Response(
            "cancelled",
            "Stopped. Any already committed cart add remains committed.",
            session_id,
            "",
        )

    def text(self, session_id: str, text: str) -> Response:
        control = text.strip().casefold()
        if control in ("stop", "cancel", "/stop"):
            return self.cancel(session_id)
        if control in ("repeat", "repeat that", "/repeat"):
            return self.repeat(session_id)
        turn = self.begin(session_id)
        return self.final(session_id, Transcript(TranscriptKind.FINAL, text, turn))

    def confirmed_receipt(
        self, session_id: str, turn_id: str, receipt: Receipt
    ) -> Response:
        text = (
            f"Added {receipt.added_quantity} of {display_text(receipt.product_name)} to your local cart for "
            f"{money_text(receipt.line_price_minor, receipt.currency)}. "
            f"Quantity after this operation was {receipt.resulting_quantity}. This does not reserve stock."
        )
        return self.remember(
            Response(
                "added",
                text,
                session_id,
                turn_id,
                operation_id=receipt.operation_id,
                receipt=receipt,
            )
        )

    def retry(self, session_id: str, operation_id: str) -> Response:
        try:
            command = self.cart.load_command(session_id, operation_id)
            receipt = self.cart.add(command)
            return self.confirmed_receipt(session_id, command.turn_id, receipt)
        except OutcomeUnknown:
            return self.error(
                session_id,
                "",
                "outcome_unknown",
                "The previous add cannot be verified yet. Retry this same operation; do not submit a replacement add.",
            )
        except (CartError, SessionError):
            return self.error(
                session_id,
                "",
                "retry_rejected",
                "That operation is cancelled, invalid or expired. No new add was dispatched.",
            )
        except (DatabaseUnavailable, psycopg.Error):
            return self.error(
                session_id,
                "",
                "database_unavailable",
                "The database is unavailable. The previous operation still needs verification.",
            )

    def _add(self, session_id: str, turn_id: str, intent: Intent) -> Response:
        pending = self.cart.pending(session_id)
        if pending:
            return self.remember(
                Response(
                    "outcome_pending",
                    "Resolve or retry the previous operation before requesting another add.",
                    session_id,
                    turn_id,
                    operation_id=pending,
                )
            )
        constraints = intent.constraints or (
            intent.search.constraints
            if intent.search
            else HardConstraints("INR", quantity=intent.quantity)
        )
        if intent.ordinal is not None:
            offer = self.sessions.resolve(session_id, intent.ordinal)
            command = AddCommand(
                session_id,
                turn_id,
                str(uuid.uuid4()),
                "exact",
                SearchRequest(constraints),
                offer.variant_id,
                offer.catalogue_revision,
                offer.unit_price_minor,
            )
        elif (
            intent.search is not None
            and intent.objective == "cheapest"
            and intent.search.route is RetrievalRoute.STRUCTURED
        ):
            command = AddCommand(
                session_id, turn_id, str(uuid.uuid4()), "cheapest", intent.search
            )
        elif intent.search is not None and intent.search.route is RetrievalRoute.EXACT:
            result = self.catalogue.search(intent.search)
            if len(result.matches) != 1:
                return self.present(
                    session_id,
                    turn_id,
                    intent.search,
                    "Choose an eligible variant before adding it.",
                )
            item = result.matches[0]
            if item.variant.price is None:
                raise CartError("current_price_not_verified")
            command = AddCommand(
                session_id,
                turn_id,
                str(uuid.uuid4()),
                "exact",
                intent.search,
                item.variant.variant_id,
                result.catalogue_revision,
                item.variant.price.minor_units,
            )
        else:
            if intent.search is None:
                raise InterpretationError(
                    "Please identify a current result or exact variant."
                )
            return self.present(
                session_id,
                turn_id,
                intent.search,
                "Please choose a specific result. I cannot automatically add an unverified best or subjective cheapest match.",
            )
        with self._guard:
            cancelled = self._events.get(session_id)
        try:
            receipt = self.cart.add(command, cancelled=cancelled)
            try:
                return self.confirmed_receipt(session_id, turn_id, receipt)
            except (ValueError, TypeError):
                return self.remember(
                    Response(
                        "added",
                        "The local add committed. Read or retry this operation's receipt for details; do not repeat the add.",
                        session_id,
                        turn_id,
                        operation_id=receipt.operation_id,
                        receipt=receipt,
                    )
                )
        except OutcomeUnknown:
            return self.remember(
                Response(
                    "outcome_unknown",
                    "The cart outcome cannot be verified. Use Retry with this operation ID; do not create a replacement add.",
                    session_id,
                    turn_id,
                    operation_id=command.operation_id,
                )
            )

    def present(
        self, session_id: str, turn_id: str, request: SearchRequest, prefix: str = ""
    ) -> Response:
        self.sessions.invalidate_results(session_id, turn_id)
        result = self.catalogue.search(request)
        if not self.sessions.is_active(session_id, turn_id):
            return Response("cancelled", "", session_id, turn_id)
        if not result.matches:
            text = (
                "No eligible products were found in the complete declared catalogue."
                if result.can_claim_no_match
                else "I cannot verify an eligible match from the available catalogue data. Please refine the request or refresh the source."
            )
            return self.error(
                session_id,
                turn_id,
                "no_match" if result.can_claim_no_match else "incomplete",
                text,
            )
        listing = self.sessions.publish_results(session_id, turn_id, result)
        if listing is None:
            return self.error(
                session_id,
                turn_id,
                "incomplete",
                "No presentable verified offer is available.",
            )
        parts = [prefix] if prefix else []
        if request.route is RetrievalRoute.DISCOVERY:
            parts.append(
                "Related candidates follow. Subjective suitability is unverified; lowest price refers only to evaluated literal-term matches."
            )
        elif result.status is SearchStatus.INCOMPLETE:
            parts.append(
                "Catalogue information is incomplete; a global cheapest claim cannot be verified."
            )
        if result.cheapest_qualifying_match is None:
            parts.append(
                "A qualifying lowest-price option could not be verified for this query."
            )
        for index, offer in enumerate(listing.offers, 1):
            details = ", ".join(
                display_text(value) for value in (offer.colour, offer.size) if value
            )
            role = ", lowest price in the stated scope" if offer.cheapest else ""
            parts.append(
                f"{index}. {display_text(offer.product_name)}{', ' + details if details else ''}, {money_text(offer.unit_price_minor, offer.currency)}{role}."
            )
        parts.append(
            "After the complete list is read, select by its result number. Stop interrupts speech; Repeat reads the response again."
        )
        return self.remember(
            Response("results", " ".join(parts), session_id, turn_id, listing)
        )

    def final(self, session_id: str, transcript: Transcript) -> Response:
        turn_id = transcript.turn_id
        try:
            if not self.sessions.is_active(session_id, turn_id):
                return Response("cancelled", "", session_id, turn_id)
            if transcript.kind is TranscriptKind.PARTIAL:
                return Response("partial", "", session_id, turn_id)
            if not transcript.can_authorize_action:
                return self.error(
                    session_id,
                    turn_id,
                    "no_speech",
                    "No usable speech was heard. Please try again.",
                )
            if not self.sessions.claim_final(session_id, turn_id):
                previous = self.repeat(session_id)
                return (
                    previous
                    if previous.turn_id == turn_id
                    else Response(
                        "busy",
                        "This final turn is already being handled.",
                        session_id,
                        turn_id,
                    )
                )
            control = transcript.text.strip().casefold()
            if control in ("repeat", "repeat that", "say that again"):
                return replace(self.repeat(session_id), turn_id=turn_id)
            if control in ("stop", "cancel", "never mind"):
                return self.cancel(session_id)
            state = self.database.inspect()
            if not state["populated"]:
                return self.error(
                    session_id,
                    turn_id,
                    "catalogue_not_populated",
                    "The product catalogue has not been populated. Ask the owner to import the real catalogue; no demo products are loaded.",
                )
            if state["valid_until"] is None or state["valid_until"] <= datetime.now(
                UTC
            ):
                return self.error(
                    session_id,
                    turn_id,
                    "catalogue_stale",
                    "Catalogue prices and availability have expired. Refresh the source before an add can be verified.",
                )
            if self.interpreter is None:
                return self.error(
                    session_id,
                    turn_id,
                    "model_unconfigured",
                    "Local language inference is not configured. Set a verified local model and digest before using natural-language shopping.",
                )
            intent = self.interpreter.interpret(
                transcript.text, self.database.vocabulary()
            )
            if not self.sessions.is_active(session_id, turn_id):
                return Response("cancelled", "", session_id, turn_id)
            if self.database.inspect()["revision"] != state["revision"]:
                return self.error(
                    session_id,
                    turn_id,
                    "catalogue_updating",
                    "The catalogue changed while interpreting. Please repeat the request against the current source.",
                )
            if intent.kind == "cancel":
                return self.cancel(session_id)
            if intent.kind == "repeat":
                return self.repeat(session_id)
            if intent.explicit_add:
                return self._add(session_id, turn_id, intent)
            if intent.search is None:
                raise InterpretationError("What product should I search for?")
            return self.present(session_id, turn_id, intent.search)
        except SessionError:
            return self.error(
                session_id,
                turn_id,
                "reference_unavailable",
                "Search again and read or replay the complete current list before choosing a result number. No new add was confirmed.",
            )
        except InterpretationError:
            return self.error(
                session_id,
                turn_id,
                "clarify",
                "I cannot safely resolve that request or result reference. Please clarify the product, amount, quantity or current result number.",
            )
        except CartError as exc:
            code = exc.code
            text = (
                "The offer or eligibility changed. Search again before adding."
                if "offer_changed" in code
                else "The add was not confirmed. Check the current product, quantity and available stock before retrying."
            )
            return self.error(session_id, turn_id, "add_rejected", text)
        except (TypeError, ValueError):
            return self.error(
                session_id,
                turn_id,
                "response_error",
                "The response could not be prepared safely. Please rephrase; no new add was confirmed.",
            )
        except (LocalServiceError, TimeoutError):
            return self.error(
                session_id,
                turn_id,
                "inference_unavailable",
                "Local inference is unavailable or timed out. No new cart add was confirmed. Please retry when the runtime is ready.",
            )
        except (DatabaseUnavailable, psycopg.Error):
            return self.error(
                session_id,
                turn_id,
                "database_unavailable",
                "The database is unavailable. This is not a no-match result. If an add was pending, retry its original operation ID to verify the outcome.",
            )
