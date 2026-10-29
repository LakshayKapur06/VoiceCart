"""Exact and exhaustive structured selection over an immutable authority snapshot."""

from __future__ import annotations

from collections.abc import Iterable
from types import MappingProxyType
from typing import Protocol

from voicecart.domain import (
    CatalogueItem,
    ClaimScope,
    Coverage,
    Eligibility,
    ExactIdentifier,
    Freshness,
    HardConstraints,
    IdentifierKind,
    IssueCode,
    Product,
    Qualification,
    RetrievalRoute,
    SearchIssue,
    SearchRequest,
    SearchResult,
    SearchStatus,
    Variant,
    require_text,
)
from voicecart.ranking import RankingPolicy, rank_qualified


class Catalogue(Protocol):
    """Later adapters must preserve full-source coverage and snapshot semantics."""

    def lookup(self, identifier: ExactIdentifier) -> tuple[CatalogueItem, ...]:
        """Resolve identity only; this does not authorize purchase or assert eligibility."""
        ...

    def search(
        self, request: SearchRequest, *, ranking_policy: RankingPolicy | None = None
    ) -> SearchResult: ...


def qualify(item: CatalogueItem, constraints: HardConstraints) -> Qualification:
    """Combine predicates as three-valued AND: a known false dominates unknowns."""
    product, variant = item.product, item.variant
    rejected: list[SearchIssue] = []
    unknown: list[SearchIssue] = []

    def issue(code: IssueCode, detail: str) -> SearchIssue:
        return SearchIssue(code, detail, variant.variant_id)

    if not product.active or not variant.active:
        rejected.append(issue(IssueCode.INACTIVE, "Product or variant is inactive"))
    for field, actual in (
        ("category", product.category),
        ("colour", variant.colour),
        ("size", variant.size),
    ):
        expected = getattr(constraints, field)
        if expected is None:
            continue
        if actual is None:
            unknown.append(issue(IssueCode.UNKNOWN_ATTRIBUTE, f"Unknown {field}"))
        elif actual != expected:
            rejected.append(issue(IssueCode.ATTRIBUTE_MISMATCH, f"Different {field}"))

    if variant.available is False:
        rejected.append(issue(IssueCode.UNAVAILABLE, "Variant is not available"))
    elif variant.available is None:
        unknown.append(issue(IssueCode.UNKNOWN_AVAILABILITY, "Availability is unknown"))
    if variant.stock_quantity is not None:
        if variant.stock_quantity < constraints.quantity:
            rejected.append(
                issue(IssueCode.INSUFFICIENT_STOCK, "Insufficient quantity")
            )
    elif constraints.quantity > 1:
        unknown.append(issue(IssueCode.UNKNOWN_STOCK, "Multi-unit stock is unknown"))

    if variant.price is None:
        unknown.append(issue(IssueCode.MISSING_PRICE, "Price/currency is missing"))
    elif variant.price_freshness is not Freshness.CURRENT:
        code = (
            IssueCode.STALE_PRICE
            if variant.price_freshness is Freshness.STALE
            else IssueCode.UNKNOWN_PRICE_FRESHNESS
        )
        unknown.append(issue(code, "A current price is not verified"))
    elif variant.price.currency != constraints.currency:
        rejected.append(issue(IssueCode.CURRENCY_MISMATCH, "Different currency"))
    elif constraints.price_limit is not None:
        if not constraints.price_limit.permits(variant.price):
            rejected.append(issue(IssueCode.OVER_BUDGET, "Unit price fails budget"))

    if rejected:
        return Qualification(Eligibility.REJECTED, tuple(rejected + unknown))
    if unknown:
        return Qualification(Eligibility.UNKNOWN, tuple(unknown))
    return Qualification(Eligibility.QUALIFIED)


class InMemoryCatalogue:
    """Read-only snapshot. COMPLETE means an explicit assertion about this source only.

    Never label a semantic shortlist COMPLETE. A later DB adapter must implement
    this contract against the whole declared source and a consistent snapshot.
    """

    def __init__(
        self,
        products: Iterable[Product],
        variants: Iterable[Variant],
        *,
        revision: str,
        coverage: Coverage = Coverage.UNKNOWN,
    ) -> None:
        require_text(revision, "catalogue revision")
        if not isinstance(coverage, Coverage):
            raise TypeError("coverage must be Coverage")
        product_map = {}
        for product in products:
            if not isinstance(product, Product):
                raise TypeError("catalogue requires Product records")
            if product.product_id in product_map:
                raise ValueError(f"Duplicate product ID: {product.product_id}")
            product_map[product.product_id] = product
        items = {}
        skus = set()
        for variant in variants:
            if not isinstance(variant, Variant):
                raise TypeError("catalogue requires Variant records")
            if variant.variant_id in items:
                raise ValueError(f"Duplicate variant ID: {variant.variant_id}")
            if variant.product_id not in product_map:
                raise ValueError(f"Unknown parent product: {variant.product_id}")
            if variant.sku is not None:
                if variant.sku in skus:
                    raise ValueError(f"Duplicate SKU: {variant.sku}")
                skus.add(variant.sku)
            items[variant.variant_id] = CatalogueItem(
                product_map[variant.product_id], variant
            )
        parents_with_variants = {item.product.product_id for item in items.values()}
        self._products_without_variants = tuple(
            product
            for product in product_map.values()
            if product.product_id not in parents_with_variants
        )
        self._items = MappingProxyType(items)
        self._revision = revision
        self._coverage = coverage

    @property
    def revision(self) -> str:
        return self._revision

    @property
    def coverage(self) -> Coverage:
        return self._coverage

    def lookup(self, identifier: ExactIdentifier) -> tuple[CatalogueItem, ...]:
        if not isinstance(identifier, ExactIdentifier):
            raise TypeError("lookup requires ExactIdentifier")
        fields = {
            IdentifierKind.VARIANT_ID: lambda item: item.variant.variant_id,
            IdentifierKind.SKU: lambda item: item.variant.sku,
            IdentifierKind.PRODUCT_ID: lambda item: item.product.product_id,
            IdentifierKind.MODEL_NUMBER: lambda item: item.product.model_number,
        }
        get_id = fields[identifier.kind]
        return tuple(
            self._items[key]
            for key in sorted(self._items)
            if get_id(self._items[key]) == identifier.value
        )

    def search(
        self, request: SearchRequest, *, ranking_policy: RankingPolicy | None = None
    ) -> SearchResult:
        if not isinstance(request, SearchRequest):
            raise TypeError("search requires SearchRequest")
        if request.route is RetrievalRoute.DISCOVERY:
            return SearchResult(
                request=request,
                catalogue_revision=self.revision,
                status=SearchStatus.UNSUPPORTED,
                scope=ClaimScope.UNVERIFIED,
                issues=(
                    SearchIssue(IssueCode.UNSUPPORTED_ROUTE, "Discovery is planned"),
                ),
            )
        # Sorting IDs stabilizes presentation without claiming relevance ranking.
        if request.route is RetrievalRoute.EXACT:
            if request.identifier is None:
                raise ValueError("Exact lookup requires an identifier")
            universe = self.lookup(request.identifier)
        else:
            universe = tuple(self._items[key] for key in sorted(self._items))
        qualified: list[CatalogueItem] = []
        issues: list[SearchIssue] = []
        for product in self._products_without_variants:
            if not product.active:
                continue
            if (
                request.constraints.category is not None
                and product.category is not None
                and product.category != request.constraints.category
            ):
                continue
            if request.identifier is not None:
                if (
                    request.identifier.kind is IdentifierKind.PRODUCT_ID
                    and request.identifier.value != product.product_id
                ):
                    continue
                if (
                    request.identifier.kind is IdentifierKind.MODEL_NUMBER
                    and product.model_number is not None
                    and request.identifier.value != product.model_number
                ):
                    continue
                if (
                    request.identifier.kind
                    in (IdentifierKind.VARIANT_ID, IdentifierKind.SKU)
                    and universe
                ):
                    continue
            issues.append(
                SearchIssue(
                    IssueCode.UNKNOWN_ATTRIBUTE,
                    "An active potentially matching product lacks variant data",
                )
            )
        for item in universe:
            assessment = qualify(item, request.constraints)
            if assessment.state is Eligibility.QUALIFIED:
                qualified.append(item)
            elif assessment.state is Eligibility.UNKNOWN:
                issues.extend(assessment.issues)
        if self.coverage is not Coverage.COMPLETE:
            code = (
                IssueCode.PARTIAL_COVERAGE
                if self.coverage is Coverage.PARTIAL
                else IssueCode.UNKNOWN_COVERAGE
            )
            issues.append(
                SearchIssue(code, "Complete source coverage is not established")
            )

        matches = tuple(qualified)
        if issues:
            status = SearchStatus.INCOMPLETE
            scope = ClaimScope.VERIFIED_RECORDS if matches else ClaimScope.UNVERIFIED
        else:
            status = SearchStatus.MATCHES if matches else SearchStatus.NO_MATCH
            scope = (
                ClaimScope.EXACT_IDENTIFIER
                if request.route is RetrievalRoute.EXACT
                else ClaimScope.COMPLETE_CATALOGUE
            )

        def price_key(item: CatalogueItem) -> tuple[int, str]:
            if item.variant.price is None:
                raise ValueError("Qualified item must have a price")
            return item.variant.price.minor_units, item.variant.variant_id

        cheapest = min(
            matches,
            key=price_key,
            default=None,
        )
        version, ranked = (
            rank_qualified(ranking_policy, request, matches)
            if ranking_policy is not None
            else (None, ())
        )
        return SearchResult(
            request=request,
            catalogue_revision=self.revision,
            status=status,
            scope=scope,
            matches=matches,
            cheapest_qualifying_match=cheapest,
            ranked_matches=ranked,
            ranking_policy_version=version,
            issues=tuple(issues),
        )
