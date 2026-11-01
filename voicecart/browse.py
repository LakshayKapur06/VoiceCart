"""Read-only metadata discovery; unknown historical offers never become cart facts."""

from __future__ import annotations

from voicecart.catalogue import qualify
from voicecart.domain import Eligibility, HardConstraints
from voicecart.search import query_terms


class CatalogueBrowser:
    def __init__(self, database):
        self.database = database

    def search(
        self,
        query="",
        *,
        brand="",
        category="",
        currency=None,
        under=None,
        inclusive=False,
        offset=0,
        limit=24,
    ):
        if (
            not isinstance(query, str)
            or len(query) > 1000
            or type(offset) is not int
            or offset < 0
            or type(limit) is not int
            or not 1 <= limit <= 100
        ):
            raise ValueError("Invalid query/pagination")
        if under is not None and (
            type(under) is not int or not 0 <= under <= 2**63 - 1 or not currency
        ):
            raise ValueError("Explicit currency and integer minor-unit bound required")
        terms = " ".join(sorted(query_terms(query)))
        with self.database.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            snapshot = self.database.snapshot_in(connection)
            rows = list(
                connection.execute(
                    "SELECT p.product_id,p.name,p.category,v.variant_id,v.price_minor,v.currency,v.price_freshness,v.available,v.stock_quantity,v.colour,v.size,COALESCE(m.payload,'{}'::jsonb) AS metadata,ts_rank_cd(s.lexical_document,plainto_tsquery('simple',%s)) AS score FROM products p JOIN variants v USING(product_id) JOIN variant_search s USING(variant_id) LEFT JOIN product_metadata m USING(product_id) WHERE p.active AND v.active AND (%s='' OR s.lexical_document @@ plainto_tsquery('simple',%s)) AND (%s='' OR lower(m.payload->>'brand')=lower(%s)) AND (%s='' OR p.category=%s) AND (%s::text IS NULL OR COALESCE(v.currency,m.payload->>'price_currency')=%s)",
                    (
                        terms,
                        terms,
                        terms,
                        brand,
                        brand,
                        category,
                        category,
                        currency,
                        currency,
                    ),
                )
            )
        if under is not None:
            rows = [
                row
                for row in rows
                if row["price_minor"] is not None
                and (
                    row["price_minor"] <= under
                    if inclusive
                    else row["price_minor"] < under
                )
            ]
        rows.sort(
            key=lambda row: (
                -float(row["score"]),
                row["name"].casefold(),
                row["variant_id"],
            )
        )
        cheapest = (
            min(
                (row for row in rows if row["price_minor"] is not None),
                key=lambda row: (row["price_minor"], row["variant_id"]),
                default=None,
            )
            if currency
            else None
        )
        items_by_id = {item.variant.variant_id: item for item in snapshot.items}

        def present(row):
            item = items_by_id[row["variant_id"]]
            qualification = qualify(
                item, HardConstraints(row["currency"] or currency or "INR")
            )
            return {
                **dict(row),
                "score": float(row["score"]),
                "can_add": qualification.state is Eligibility.QUALIFIED,
                "historical": bool(row["metadata"].get("historical")),
                "revision": snapshot.state["revision"],
            }

        return {
            "items": [present(row) for row in rows[offset : offset + limit]],
            "total": len(rows),
            "offset": offset,
            "limit": limit,
            "revision": snapshot.state["revision"],
            "coverage": snapshot.state["coverage"],
            "cheapest": present(cheapest) if cheapest else None,
            "cheapest_scope": "Historical/verified metadata prices among all matching imported records; never a live global minimum",
            "can_claim_global_minimum": False,
        }
