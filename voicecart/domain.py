"""Small validated, immutable contracts; no interpretation or inference lives here."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

ProductId = NewType("ProductId", str)
VariantId = NewType("VariantId", str)
MAX_MINOR_UNITS = 2**63 - 1


def require_text(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if not value.strip():
        raise ValueError(f"{field} must not be blank")


def require_integer(value: int, field: str, minimum: int = 0) -> None:
    # bool is an int subclass; accepting True as a price or quantity is a bug.
    if type(value) is not int:
        raise TypeError(f"{field} must be an integer, not a bool or float")
    if not minimum <= value <= MAX_MINOR_UNITS:
        raise ValueError(f"{field} must be between {minimum} and {MAX_MINOR_UNITS}")


def require_currency(value: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[A-Z]{3}", value) is None:
        raise ValueError("currency must be an explicit three-letter uppercase code")


class PriceOperator(StrEnum):
    LT = "lt"
    LTE = "lte"


class Coverage(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class Freshness(StrEnum):
    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"


class RetrievalRoute(StrEnum):
    EXACT = "exact"
    STRUCTURED = "structured"
    DISCOVERY = "discovery"


class IdentifierKind(StrEnum):
    VARIANT_ID = "variant_id"
    SKU = "sku"
    PRODUCT_ID = "product_id"
    MODEL_NUMBER = "model_number"


class Eligibility(StrEnum):
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class SearchStatus(StrEnum):
    MATCHES = "matches"
    NO_MATCH = "no_match"
    INCOMPLETE = "incomplete"
    UNSUPPORTED = "unsupported"


class ClaimScope(StrEnum):
    COMPLETE_CATALOGUE = "complete_structured_catalogue"
    EXACT_IDENTIFIER = "complete_identifier_set"
    VERIFIED_RECORDS = "verified_records_only"
    UNVERIFIED = "unverified"


class IssueCode(StrEnum):
    INACTIVE = "inactive"
    ATTRIBUTE_MISMATCH = "attribute_mismatch"
    UNKNOWN_ATTRIBUTE = "unknown_required_attribute"
    MISSING_PRICE = "missing_price"
    STALE_PRICE = "stale_price"
    UNKNOWN_PRICE_FRESHNESS = "unknown_price_freshness"
    CURRENCY_MISMATCH = "currency_mismatch"
    OVER_BUDGET = "over_budget"
    UNAVAILABLE = "unavailable"
    UNKNOWN_AVAILABILITY = "unknown_availability"
    INSUFFICIENT_STOCK = "insufficient_stock"
    UNKNOWN_STOCK = "unknown_stock_quantity"
    PARTIAL_COVERAGE = "partial_coverage"
    UNKNOWN_COVERAGE = "unknown_coverage"
    UNSUPPORTED_ROUTE = "unsupported_route"


@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: str

    def __post_init__(self) -> None:
        require_integer(self.minor_units, "minor_units")
        require_currency(self.currency)


@dataclass(frozen=True)
class PriceLimit:
    amount: Money
    operator: PriceOperator

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Money):
            raise TypeError("price limit requires Money")
        if not isinstance(self.operator, PriceOperator):
            raise TypeError("operator must be PriceOperator.LT or PriceOperator.LTE")

    def permits(self, price: Money) -> bool:
        if price.currency != self.amount.currency:
            return False
        if self.operator is PriceOperator.LT:
            return price.minor_units < self.amount.minor_units
        return price.minor_units <= self.amount.minor_units


@dataclass(frozen=True)
class Product:
    product_id: ProductId
    name: str
    category: str | None = None
    model_number: str | None = None
    description: str = ""
    active: bool = True

    def __post_init__(self) -> None:
        require_text(self.product_id, "product_id")
        require_text(self.name, "name")
        for field in ("category", "model_number"):
            value = getattr(self, field)
            if value is not None:
                require_text(value, field)
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        if type(self.active) is not bool:
            raise TypeError("active must be bool")


@dataclass(frozen=True)
class Variant:
    variant_id: VariantId
    product_id: ProductId
    price: Money | None = None
    colour: str | None = None
    size: str | None = None
    sku: str | None = None
    available: bool | None = None
    stock_quantity: int | None = None
    price_freshness: Freshness = Freshness.UNKNOWN
    active: bool = True

    def __post_init__(self) -> None:
        require_text(self.variant_id, "variant_id")
        require_text(self.product_id, "product_id")
        for field in ("colour", "size", "sku"):
            value = getattr(self, field)
            if value is not None:
                require_text(value, field)
        if self.price is not None and not isinstance(self.price, Money):
            raise TypeError("price must be Money or None")
        if self.available is not None and type(self.available) is not bool:
            raise TypeError("available must be bool or None")
        if self.stock_quantity is not None:
            require_integer(self.stock_quantity, "stock_quantity")
        if self.available is True and self.stock_quantity == 0:
            raise ValueError("available=True contradicts zero stock")
        if not isinstance(self.price_freshness, Freshness):
            raise TypeError("price_freshness must be Freshness")
        if type(self.active) is not bool:
            raise TypeError("active must be bool")


@dataclass(frozen=True)
class CatalogueItem:
    product: Product
    variant: Variant

    def __post_init__(self) -> None:
        if not isinstance(self.product, Product) or not isinstance(
            self.variant, Variant
        ):
            raise TypeError("CatalogueItem requires a validated Product and Variant")
        if self.variant.product_id != self.product.product_id:
            raise ValueError("variant must belong to the supplied product")


@dataclass(frozen=True)
class HardConstraints:
    currency: str
    category: str | None = None
    colour: str | None = None
    size: str | None = None
    price_limit: PriceLimit | None = None
    quantity: int = 1

    def __post_init__(self) -> None:
        require_currency(self.currency)
        for field in ("category", "colour", "size"):
            value = getattr(self, field)
            if value is not None:
                require_text(value, field)
        require_integer(self.quantity, "quantity", minimum=1)
        if self.price_limit is not None:
            if not isinstance(self.price_limit, PriceLimit):
                raise TypeError("price_limit must be PriceLimit or None")
            if self.price_limit.amount.currency != self.currency:
                raise ValueError("budget and search currency must agree")


@dataclass(frozen=True)
class ExactIdentifier:
    kind: IdentifierKind
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, IdentifierKind):
            raise TypeError("kind must be IdentifierKind")
        require_text(self.value, "identifier value")


@dataclass(frozen=True)
class SearchRequest:
    constraints: HardConstraints
    route: RetrievalRoute = RetrievalRoute.STRUCTURED
    identifier: ExactIdentifier | None = None
    semantic_query: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.constraints, HardConstraints):
            raise TypeError("constraints must be HardConstraints")
        if not isinstance(self.route, RetrievalRoute):
            raise TypeError("route must be RetrievalRoute")
        if self.route is RetrievalRoute.EXACT:
            if not isinstance(self.identifier, ExactIdentifier):
                raise ValueError("exact lookup requires a typed identifier")
        elif self.identifier is not None:
            raise ValueError("identifier belongs only to an exact request")
        if self.route is RetrievalRoute.DISCOVERY:
            require_text(self.semantic_query, "semantic_query")
        elif self.semantic_query is not None:
            raise ValueError("descriptive text must use the discovery route")


@dataclass(frozen=True)
class SearchIssue:
    code: IssueCode
    detail: str
    variant_id: VariantId | None = None


@dataclass(frozen=True)
class Qualification:
    state: Eligibility
    issues: tuple[SearchIssue, ...] = ()


@dataclass(frozen=True)
class SearchResult:
    request: SearchRequest
    catalogue_revision: str
    status: SearchStatus
    scope: ClaimScope
    matches: tuple[CatalogueItem, ...] = ()
    cheapest_qualifying_match: CatalogueItem | None = None
    ranked_matches: tuple[CatalogueItem, ...] = ()
    ranking_policy_version: str | None = None
    issues: tuple[SearchIssue, ...] = ()

    @property
    def overall_match(self) -> CatalogueItem | None:
        """No policy means unevaluated relevance, not an invented winner."""
        return self.ranked_matches[0] if self.ranked_matches else None

    @property
    def can_claim_catalogue_minimum(self) -> bool:
        return (
            self.scope is ClaimScope.COMPLETE_CATALOGUE
            and self.cheapest_qualifying_match is not None
        )

    @property
    def can_claim_no_match(self) -> bool:
        return self.status is SearchStatus.NO_MATCH and self.scope in (
            ClaimScope.COMPLETE_CATALOGUE,
            ClaimScope.EXACT_IDENTIFIER,
        )
