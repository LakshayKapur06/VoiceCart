"""Snapshot-consistent exact/structured and lexical+dense discovery.

The provisional scorer is inspectable, not an established human relevance model.
Discovery never upgrades model similarity into a global minimum/no-match proof.
"""

from __future__ import annotations

import re
from dataclasses import replace

from voicecart.database import Database
from voicecart.domain import (
    CatalogueItem,
    ClaimScope,
    IssueCode,
    RetrievalRoute,
    SearchIssue,
    SearchRequest,
    SearchResult,
    SearchStatus,
)
from voicecart.embeddings import OllamaEncoder, vector_literal
from voicecart.local_http import LocalServiceError
from voicecart.ranking import RankingPolicy, rank_qualified

STOP_WORDS = set(
    "cheap affordable inexpensive budget a an the me my please find show search for and or to in of with good best cheapest lowest price least expensive under below less than at most up no more not add put it them cart rupee rupees inr rs each per unit item total altogether combined".split()
)


def query_terms(text: str) -> set[str]:
    return {
        word.casefold()
        for word in re.findall(r"[^\W_]+", text)
        if not word.isdecimal() and word.casefold() not in STOP_WORDS
    }


def item_price(item: CatalogueItem) -> int:
    if item.variant.price is None:
        raise ValueError("Qualified candidate lacks price")
    return item.variant.price.minor_units


class PostgresCatalogue:
    POLICY_VERSION = "experimental-exhaustive-hybrid-v2-price-scale-100000"

    def __init__(self, database: Database, encoder: OllamaEncoder | None = None):
        self.database, self.encoder = database, encoder

    def lookup(self, identifier):
        return self.database.snapshot().catalogue.lookup(identifier)

    def search(
        self, request: SearchRequest, *, ranking_policy: RankingPolicy | None = None
    ) -> SearchResult:
        if request.route is not RetrievalRoute.DISCOVERY:
            return self.database.snapshot().catalogue.search(
                request, ranking_policy=ranking_policy
            )
        terms = query_terms(request.semantic_query or "")
        if not terms:
            return SearchResult(
                request,
                "unverified",
                SearchStatus.UNSUPPORTED,
                ClaimScope.UNVERIFIED,
                issues=(
                    SearchIssue(
                        IssueCode.UNSUPPORTED_ROUTE,
                        "Please name the product or a specific purpose.",
                    ),
                ),
            )
        vector = None
        semantic_issue = "Semantic model is not configured; lexical evidence only."
        if self.encoder is not None:
            try:
                vector = self.encoder.encode(
                    [request.semantic_query or ""], query=True
                )[0]
                semantic_issue = ""
            except (LocalServiceError, ValueError, TimeoutError):
                semantic_issue = "Semantic service unavailable; lexical evidence only."
        with self.database.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            snapshot = self.database.snapshot_in(connection)
            structured = snapshot.catalogue.search(
                replace(request, route=RetrievalRoute.STRUCTURED, semantic_query=None)
            )
            lexical = {
                row["variant_id"]: float(row["score"])
                for row in connection.execute(
                    "SELECT variant_id,ts_rank_cd(lexical_document,plainto_tsquery('simple',%s)) AS score FROM variant_search",
                    (" ".join(sorted(terms)),),
                )
            }
            documents = {
                row["variant_id"]: row["document"]
                for row in connection.execute(
                    "SELECT variant_id,document FROM variant_search"
                )
            }
            dense = {}
            if vector is not None and self.encoder is not None:
                if snapshot.state["generation"] != self.encoder.spec.generation:
                    semantic_issue = "Encoder generation differs from the publication; re-import before semantic search."
                else:
                    dense = {
                        row["variant_id"]: float(row["similarity"])
                        for row in connection.execute(
                            "SELECT variant_id,1-(embedding <=> %s::vector) AS similarity FROM variant_search WHERE generation=%s ORDER BY embedding <=> %s::vector,variant_id",
                            (
                                vector_literal(vector),
                                self.encoder.spec.generation,
                                vector_literal(vector),
                            ),
                        )
                    }
        scores = {}
        literal_matches = []
        candidates = []
        for item in structured.matches:
            identifier = item.variant.variant_id
            words = query_terms(documents.get(identifier, ""))
            coverage = len(terms & words) / len(terms)
            # The low-price branch cannot introduce an unrelated zero-evidence item.
            if coverage == 0 and dense.get(identifier, 0.0) <= 0:
                continue
            if coverage == 1:
                literal_matches.append(item)
            title_words = query_terms(item.product.name)
            title_fit = len(terms & title_words) / len(terms)
            semantic = max(0.0, min(1.0, (dense.get(identifier, -1.0) + 1.0) / 2.0))
            price_utility = 1.0 / (1.0 + item_price(item) / 100000.0)
            # Literal coverage is a preceding tier: price cannot rescue an
            # accessory that lacks the requested terms. Weights are experimental.
            scores[identifier] = (
                coverage,
                0.65 * title_fit + 0.25 * semantic + 0.10 * price_utility,
                lexical.get(identifier, 0.0),
            )
            candidates.append(item)
        matches = tuple(sorted(candidates, key=lambda item: item.variant.variant_id))
        ranked = tuple(
            sorted(
                matches,
                key=lambda item: (
                    -scores[item.variant.variant_id][0],
                    -scores[item.variant.variant_id][1],
                    -scores[item.variant.variant_id][2],
                    item.variant.variant_id,
                ),
            )
        )
        version = self.POLICY_VERSION
        if ranking_policy is not None:
            version, ranked = rank_qualified(ranking_policy, request, matches)
        cheapest = min(
            literal_matches,
            key=lambda item: (item_price(item), item.variant.variant_id),
            default=None,
        )
        issues = list(structured.issues)
        issues.append(
            SearchIssue(
                IssueCode.UNSUPPORTED_ROUTE,
                "Discovery suggests related products; subjective suitability and a catalogue-wide cheapest are unverified. Lowest price is scoped to evaluated literal-term matches.",
            )
        )
        if semantic_issue:
            issues.append(SearchIssue(IssueCode.UNSUPPORTED_ROUTE, semantic_issue))
        return SearchResult(
            request,
            snapshot.state["revision"],
            SearchStatus.INCOMPLETE,
            ClaimScope.VERIFIED_RECORDS if matches else ClaimScope.UNVERIFIED,
            matches,
            cheapest,
            ranked,
            version,
            tuple(issues),
        )
