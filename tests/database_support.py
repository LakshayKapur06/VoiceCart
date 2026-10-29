"""Destructive fixtures require the test runner's owned, temporary database."""

import os
import re
import unittest
from pathlib import Path

from voicecart.database import Database, parse_local_dsn


def isolated_database() -> Database:
    dsn = os.environ.get("VOICECART_TEST_DSN")
    root = os.environ.get("VOICECART_TEST_ROOT")
    if not dsn or not root:
        raise unittest.SkipTest(
            "Use scripts/verify.py --postgres for isolated real-service tests"
        )
    config = parse_local_dsn(dsn)
    owned = Path(root).resolve()
    host = Path(config["host"]).resolve()
    if (
        not owned.name.startswith("vcpg-")
        or not host.is_relative_to(owned)
        or not re.fullmatch(r"vc_test_[a-f0-9]{16}", config["dbname"])
        or (owned / ".voicecart-test-owner").read_text() != config["dbname"]
    ):
        raise RuntimeError(
            "Refusing fixtures outside the runner-owned temporary database"
        )
    return Database(dsn)


def fabricated_document(revision="fixture-1", previous="unpopulated"):
    return {
        "schema_version": 1,
        "revision": revision,
        "previous_revision": previous,
        "coverage": "complete",
        "source": "FABRICATED AUTOMATED TEST DATA ONLY",
        "valid_until": "2099-01-01T00:00:00+00:00",
        "products": [
            {
                "product_id": "p-best",
                "name": "College backpack",
                "category": "backpack",
                "description": "Laptop space",
            },
            {
                "product_id": "p-cheap",
                "name": "Backpack",
                "category": "backpack",
                "description": "College backpack",
            },
            {
                "product_id": "p-accessory",
                "name": "Backpack charm",
                "category": "accessory",
            },
        ],
        "variants": [
            {
                "variant_id": "v-best",
                "product_id": "p-best",
                "sku": "SKU-BEST",
                "colour": "black",
                "size": "medium",
                "price": {"minor_units": 150000, "currency": "INR"},
                "available": True,
                "stock_quantity": 8,
                "price_freshness": "current",
            },
            {
                "variant_id": "v-cheap",
                "product_id": "p-cheap",
                "sku": "SKU-CHEAP",
                "colour": "black",
                "size": "medium",
                "price": {"minor_units": 50000, "currency": "INR"},
                "available": True,
                "stock_quantity": 3,
                "price_freshness": "current",
            },
            {
                "variant_id": "v-accessory",
                "product_id": "p-accessory",
                "price": {"minor_units": 100, "currency": "INR"},
                "available": True,
                "stock_quantity": 50,
                "price_freshness": "current",
            },
        ],
        "aliases": {"category": {"backpacks": "backpack"}},
    }
