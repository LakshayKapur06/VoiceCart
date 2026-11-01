"""Fabricated dataset rows stay in temporary test files only."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tests.database_support import fabricated_document, isolated_database
from voicecart.browse import CatalogueBrowser
from voicecart.dataset import historical_usd, normalize
from voicecart.ingestion import parse_import


class DatasetTests(unittest.TestCase):
    def test_historical_amount_equivalence_and_minor_boundaries(self):
        for value, expected in [
            ("0", 0),
            ("12.34", 1234),
            (None, None),
            (True, None),
            ("NaN", None),
            ("-1", None),
            ("1.001", None),
            ("range", None),
            ("92233720368547758.08", None),
        ]:
            with self.subTest(value=value):
                self.assertEqual(historical_usd(value), expected)

    def test_real_schema_normalization_provenance_duplicates_unknowns_and_hash(self):
        raw = {
            "parent_asin": "TEST-ONLY",
            "title": "Fabricated test appliance",
            "main_category": "test",
            "price": "4.25",
            "description": ["test"],
            "features": [],
            "details": {"Brand": "Test-only", "Size": "large"},
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.jsonl"
            path.write_text(
                "\n".join(json.dumps(row) for row in (raw, raw, {"title": "invalid"}))
            )
            manifest = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "url": "https://example.invalid/TEST-ONLY",
                "revision": "test-revision",
                "category": "test",
            }
            snapshot, report = normalize(path, manifest, "unpopulated")
            self.assertEqual(
                (report["imported"], report["duplicates"], report["rejected"]),
                (1, 1, 1),
            )
            self.assertEqual(snapshot["variants"][0]["price"]["currency"], "USD")
            self.assertIsNone(snapshot["variants"][0]["available"])
            self.assertEqual(snapshot["variants"][0]["price_freshness"], "stale")
            self.assertEqual(snapshot["metadata"]["TEST-ONLY"]["raw_price"], "4.25")
            manifest["sha256"] = "bad"
            with self.assertRaises(ValueError):
                normalize(path, manifest, "unpopulated")


class BrowserDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute("TRUNCATE variant_search,variants,products CASCADE")
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',populated=false"
            )

    def test_historical_metadata_browsable_but_cannot_add(self):
        raw = fabricated_document()
        for variant in raw["variants"]:
            variant.update(available=None, stock_quantity=None, price_freshness="stale")
        raw["variants"][0]["price"] = None
        raw["metadata"] = {
            "p-best": {
                "source_url": "https://example.invalid/TEST",
                "source_record_id": "TEST",
                "brand": "Fixture",
                "historical": True,
                "price_currency": "INR",
            }
        }
        self.database.publish(parse_import(raw))
        result = CatalogueBrowser(self.database).search(
            "backpack", currency="INR", limit=1
        )
        self.assertGreater(result["total"], 1)
        self.assertEqual(len(result["items"]), 1)
        self.assertFalse(result["items"][0]["can_add"])
        self.assertFalse(result["can_claim_global_minimum"])
        self.assertIsNotNone(result["cheapest"])
        self.assertEqual(
            CatalogueBrowser(self.database).search("", brand="Fixture", currency="INR")[
                "total"
            ],
            1,
        )
        self.assertEqual(
            CatalogueBrowser(self.database).search("", brand="Fixture")["total"], 1
        )
        with self.assertRaises(ValueError):
            CatalogueBrowser(self.database).search("", limit=101)
