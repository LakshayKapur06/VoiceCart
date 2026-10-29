"""Owner-supplied full-snapshot JSON validation; no production fixture or seed path."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from voicecart.catalogue import InMemoryCatalogue
from voicecart.domain import (
    Coverage,
    Freshness,
    Money,
    Product,
    ProductId,
    Variant,
    VariantId,
    require_text,
)
from voicecart.local_http import strict_json


class ImportValidationError(ValueError):
    def __init__(self, issues: list[str]):
        self.issues = tuple(issues)
        super().__init__("Catalogue rejected: " + "; ".join(issues))


@dataclass(frozen=True)
class CatalogueImport:
    revision: str
    previous_revision: str
    coverage: Coverage
    source: str
    valid_until: datetime
    products: tuple[Product, ...]
    variants: tuple[Variant, ...]
    aliases: dict[str, dict[str, str]]


def exact_keys(value: dict, required: set[str], optional: set[str]) -> None:
    if (
        not isinstance(value, dict)
        or not required <= set(value)
        or set(value) - required - optional
    ):
        raise ValueError("Missing or unsupported fields")


def parse_import(document: dict, *, now: datetime | None = None) -> CatalogueImport:
    issues = []
    try:
        exact_keys(
            document,
            {
                "schema_version",
                "revision",
                "previous_revision",
                "coverage",
                "source",
                "valid_until",
                "products",
                "variants",
            },
            {"aliases"},
        )
        if (
            type(document["schema_version"]) is not int
            or document["schema_version"] != 1
        ):
            raise ValueError("Unsupported schema version")
        for field in ("revision", "previous_revision", "source"):
            require_text(document[field], field)
        if (
            document["revision"] == document["previous_revision"]
            or document["revision"] == "unpopulated"
        ):
            raise ValueError("A new nonreserved revision is required")
        coverage = Coverage(document["coverage"])
        valid_until = datetime.fromisoformat(
            document["valid_until"].replace("Z", "+00:00")
        )
        if valid_until.tzinfo is None or valid_until <= (now or datetime.now(UTC)):
            raise ValueError("valid_until must be a future timestamp with timezone")
        if not isinstance(document["products"], list) or not isinstance(
            document["variants"], list
        ):
            raise ValueError("products and variants must be arrays")
        if len(document["products"]) > 100000 or len(document["variants"]) > 250000:
            raise ValueError("Snapshot exceeds the supported import size")
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        raise ImportValidationError(["manifest: " + str(exc)]) from exc
    products = []
    variants = []
    for index, row in enumerate(document["products"]):
        try:
            exact_keys(
                row,
                {"product_id", "name"},
                {"category", "model_number", "description", "active"},
            )
            if len(json.dumps(row)) > 16000:
                raise ValueError("Product document too long")
            products.append(Product(**row))
        except (TypeError, ValueError):
            issues.append(f"products[{index}]: invalid fields or values")
    for index, row in enumerate(document["variants"]):
        try:
            exact_keys(
                row,
                {"variant_id", "product_id"},
                {
                    "price",
                    "colour",
                    "size",
                    "sku",
                    "available",
                    "stock_quantity",
                    "price_freshness",
                    "active",
                },
            )
            fields = dict(row)
            if fields.get("price") is not None:
                exact_keys(fields["price"], {"minor_units", "currency"}, set())
                fields["price"] = Money(**fields["price"])
            fields["price_freshness"] = Freshness(
                fields.get("price_freshness", "unknown")
            )
            fields["variant_id"] = VariantId(fields["variant_id"])
            fields["product_id"] = ProductId(fields["product_id"])
            variants.append(Variant(**fields))
        except (TypeError, ValueError):
            issues.append(f"variants[{index}]: invalid fields or values")
    aliases = document.get("aliases", {})
    try:
        if not isinstance(aliases, dict) or set(aliases) - {
            "category",
            "colour",
            "size",
        }:
            raise ValueError("Invalid alias fields")
        for mapping in aliases.values():
            if not isinstance(mapping, dict) or len(mapping) > 500:
                raise ValueError("Invalid alias map")
            for alias, canonical in mapping.items():
                require_text(alias, "alias")
                require_text(canonical, "canonical value")
                if (
                    alias != alias.casefold()
                    or len(alias) > 100
                    or len(canonical) > 100
                ):
                    raise ValueError("Alias must be bounded and casefolded")
        InMemoryCatalogue(
            products, variants, revision=document["revision"], coverage=coverage
        )
    except (TypeError, ValueError):
        issues.append(
            "snapshot: duplicate identifiers/SKUs, orphan variants or invalid aliases"
        )
    if issues:
        raise ImportValidationError(issues)
    return CatalogueImport(
        document["revision"],
        document["previous_revision"],
        coverage,
        document["source"],
        valid_until,
        tuple(products),
        tuple(variants),
        aliases,
    )


def load_import(path: Path) -> CatalogueImport:
    if path.stat().st_size > 128 * 1024 * 1024:
        raise ImportValidationError(["File exceeds 128 MiB import limit"])
    try:
        return parse_import(strict_json(path.read_text(encoding="utf-8")))
    except (UnicodeError, ValueError) as exc:
        if isinstance(exc, ImportValidationError):
            raise
        raise ImportValidationError(["Invalid JSON or duplicate JSON keys"]) from exc


def search_document(product: Product, variant: Variant) -> str:
    # Volatile prices/stock are intentionally excluded from semantic content.
    return "\n".join(
        value
        for value in (
            product.name,
            product.category,
            product.model_number,
            variant.sku,
            variant.colour,
            variant.size,
            product.description,
        )
        if value
    )


def content_hash(document: str) -> str:
    return hashlib.sha256(document.encode("utf-8")).hexdigest()
