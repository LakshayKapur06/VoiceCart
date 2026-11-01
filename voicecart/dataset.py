"""Normalize real Amazon metadata without fabricating commercial truth."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from voicecart.ingestion import parse_import
from voicecart.local_http import strict_json


def historical_usd(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value).strip())
        if (
            not amount.is_finite()
            or amount < 0
            or amount * 100 != (amount * 100).to_integral_value()
            or amount * 100 > 2**63 - 1
        ):
            return None
        return int(amount * 100)
    except InvalidOperation:
        return None


def normalize(path: Path, manifest: dict, previous_revision: str) -> tuple[dict, dict]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("Source extract hash mismatch")
    products = []
    variants = []
    metadata = {}
    seen = set()
    report = {
        "source_rows": 0,
        "imported": 0,
        "duplicates": 0,
        "rejected": 0,
        "known_historical_prices": 0,
        "known_current_stock": 0,
        "issues": [],
        "source_sha256": digest,
        "source_url": manifest["url"],
        "source_revision": manifest["revision"],
    }
    with path.open("rb") as source:
        for index, line in enumerate(source, 1):
            report["source_rows"] += 1
            try:
                if len(line) > 2 * 1024 * 1024:
                    raise ValueError("Source row too large")
                raw = strict_json(line.decode())
                asin = raw.get("parent_asin")
                title = raw.get("title")
                if (
                    not isinstance(asin, str)
                    or not asin.strip()
                    or not isinstance(title, str)
                    or not title.strip()
                ):
                    raise ValueError("Missing source identifier/title")
                if asin in seen:
                    report["duplicates"] += 1
                    continue
                details = raw.get("details", {})
                if isinstance(details, str):
                    details = strict_json(details)
                if not isinstance(details, dict):
                    details = {}
                brand = details.get("Brand")
                if not isinstance(brand, str) or not brand.strip():
                    brand = None
                description = "\n".join(
                    str(x)
                    for key in ("description", "features")
                    for x in (raw.get(key) or [])
                    if isinstance(x, str)
                )
                if brand:
                    description += "\nBrand: " + brand
                price = historical_usd(raw.get("price"))
                product = {
                    "product_id": asin,
                    "name": title,
                    "category": raw.get("main_category") or manifest["category"],
                    "description": description,
                }
                variant = {
                    "variant_id": "metadata:" + asin,
                    "product_id": asin,
                    "price": {"minor_units": price, "currency": "USD"}
                    if price is not None
                    else None,
                    "price_freshness": "stale",
                    "available": None,
                    "stock_quantity": None,
                }
                for key, target in [("Color", "colour"), ("Size", "size")]:
                    if isinstance(details.get(key), str) and details[key].strip():
                        variant[target] = details[key]
                record = {
                    "source_url": manifest["url"],
                    "source_revision": manifest["revision"],
                    "source_record_id": asin,
                    "source_row": index,
                    "source_sha256": digest,
                    "record_sha256": hashlib.sha256(line).hexdigest(),
                    "brand": brand,
                    "attributes": details,
                    "images": raw.get("images") or [],
                    "raw_price": raw.get("price"),
                    "price_currency": "USD",
                    "historical": True,
                    "variant_semantics": "Unspecified parent metadata representation; not a verified sellable variant",
                    "raw": raw,
                }
                # Validate each record before admitting it, retaining exact source payload separately.
                candidate = {
                    "schema_version": 1,
                    "revision": "validate-" + str(index),
                    "previous_revision": "unpopulated",
                    "coverage": "partial",
                    "source": manifest["url"],
                    "valid_until": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                    "products": [product],
                    "variants": [variant],
                    "metadata": {asin: record},
                }
                parse_import(candidate)
                products.append(product)
                variants.append(variant)
                metadata[asin] = record
                seen.add(asin)
                report["imported"] += 1
                report["known_historical_prices"] += int(price is not None)
            except (ValueError, TypeError, KeyError, AttributeError) as error:
                report["rejected"] += 1
                report["issues"].append(
                    {
                        "source_row": index,
                        "code": type(error).__name__,
                        "reason": str(error)[:200],
                    }
                )
    snapshot = {
        "schema_version": 1,
        "revision": "amazon23-" + digest[:16],
        "previous_revision": previous_revision,
        "coverage": "partial",
        "source": manifest["url"],
        "valid_until": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        "products": products,
        "variants": variants,
        "metadata": metadata,
    }
    parse_import(snapshot)
    return snapshot, report


def main():
    parser = argparse.ArgumentParser(
        description="Normalize owner-requested historical metadata; never populates a database automatically."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--previous-revision", default="unpopulated")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    snapshot, report = normalize(
        args.source, strict_json(args.manifest.read_text()), args.previous_revision
    )
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False) + "\n")
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "issues"}))


if __name__ == "__main__":
    main()
