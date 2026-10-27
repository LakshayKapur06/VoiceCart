"""Evaluation seam only: hard eligibility is owned by the catalogue, not a scorer."""

from __future__ import annotations

from typing import Protocol

from voicecart.domain import CatalogueItem, SearchRequest, VariantId, require_text


class RankingContractError(ValueError):
    """A supplied policy violated the qualified-result boundary."""


class RankingPolicy(Protocol):
    @property
    def version(self) -> str:
        """Immutable identifier of an evaluated feature/weight policy."""
        ...

    def rank(
        self, request: SearchRequest, qualified: tuple[CatalogueItem, ...]
    ) -> tuple[VariantId, ...]:
        """Return a permutation of qualified IDs, without adding/removing records."""
        ...


def rank_qualified(
    policy: RankingPolicy,
    request: SearchRequest,
    qualified: tuple[CatalogueItem, ...],
) -> tuple[str, tuple[CatalogueItem, ...]]:
    version = policy.version
    try:
        require_text(version, "ranking policy version")
    except (TypeError, ValueError) as error:
        raise RankingContractError(str(error)) from error
    ordered = policy.rank(request, qualified)
    if policy.version != version:
        raise RankingContractError("policy version changed during ranking")
    if not isinstance(ordered, tuple) or any(not isinstance(x, str) for x in ordered):
        raise RankingContractError(
            "policy must return a tuple of qualified variant IDs"
        )
    by_id = {item.variant.variant_id: item for item in qualified}
    if len(ordered) != len(by_id) or set(ordered) != set(by_id):
        raise RankingContractError("policy must return every qualified ID exactly once")
    return version, tuple(by_id[variant_id] for variant_id in ordered)
