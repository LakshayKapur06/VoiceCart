"""Fabricated snapshots in a disposable real PostgreSQL/pgvector database."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from tests.database_support import fabricated_document, isolated_database
from voicecart.database import PublicationConflict, parse_local_dsn
from voicecart.domain import (
    Coverage,
    ExactIdentifier,
    HardConstraints,
    IdentifierKind,
    RetrievalRoute,
    SearchRequest,
    SearchStatus,
)
from voicecart.embeddings import EncoderSpec, OllamaEncoder, validate_vector
from voicecart.ingestion import ImportValidationError, parse_import
from voicecart.search import PostgresCatalogue


class ImportValidationTests(unittest.TestCase):
    def test_complete_valid_fixture_and_unknown_values_remain_explicit(self):
        raw = fabricated_document()
        raw["variants"][0]["price"] = None
        raw["variants"][0]["available"] = None
        bundle = parse_import(raw)
        self.assertIsNone(bundle.variants[0].price)
        self.assertIsNone(bundle.variants[0].available)

    def test_reject_duplicate_ids_skus_bad_prices_orphans_and_unknown_fields(self):
        changes = (
            lambda d: d["products"].append(d["products"][0]),
            lambda d: d["variants"][1].update(sku="SKU-BEST"),
            lambda d: d["variants"][0]["price"].update(minor_units=True),
            lambda d: d["variants"][0].update(product_id="missing"),
            lambda d: d.update(sample_data=True),
            lambda d: d.update(valid_until="2000-01-01T00:00:00Z"),
        )
        for change in changes:
            raw = fabricated_document()
            change(raw)
            with self.subTest(change=change), self.assertRaises(ImportValidationError):
                parse_import(raw)

    def test_vector_dimension_nonfinite_zero_and_mixed_types_rejected(self):
        for vector in ([0, 0], [True, 1], [float("nan"), 1], [1], [float("inf"), 1]):
            with self.subTest(vector=vector), self.assertRaises(ValueError):
                validate_vector(vector, 2)
        self.assertEqual(validate_vector([3, 4], 2), (0.6, 0.8))

    def test_database_config_cannot_redirect_to_remote_hosts(self):
        for dsn in (
            "postgresql://remote.example/owner",
            "dbname=owner hostaddr=8.8.8.8",
            "dbname=owner host=/tmp,example.com",
        ):
            with self.subTest(dsn=dsn), self.assertRaises(ValueError):
                parse_local_dsn(dsn)


class FixtureEncoder(OllamaEncoder):
    """Synthetic vector fixture, not a neural encoder."""

    def __init__(self):
        self.spec = EncoderSpec("fixture", "a" * 64, 2)

    def encode(self, texts, *, query=False):
        if query:
            return [(1.0, 0.0) for _ in texts]
        return [
            (1.0, 0.0) if text.startswith("College") else (0.8, 0.6) for text in texts
        ]


class PostgreSQLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute("TRUNCATE variant_search,variants,products CASCADE")
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',coverage='unknown',populated=false,source=NULL,valid_until=NULL,generation=NULL,dimensions=NULL,aliases='{}' WHERE singleton=true"
            )

    def publish(self, raw=None, encoder=None):
        return self.database.publish(
            parse_import(raw or fabricated_document()), encoder=encoder
        )

    def test_migrations_idempotent_empty_and_startup_inserts_no_products(self):
        self.assertEqual(self.database.migrate(), [])
        self.database.check_ready()
        state = self.database.inspect()
        self.assertEqual(state["product_count"], 0)
        self.assertEqual(state["variant_count"], 0)
        self.assertFalse(state["populated"])
        result = PostgresCatalogue(self.database).search(
            SearchRequest(HardConstraints("INR"))
        )
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertFalse(result.can_claim_no_match)
        self.assertEqual(self.database.inspect()["product_count"], 0)

    def test_real_publication_exact_structured_and_cheapest_oracle(self):
        self.publish()
        catalogue = PostgresCatalogue(self.database)
        request = SearchRequest(
            HardConstraints("INR", category="backpack", colour="black")
        )
        result = catalogue.search(request)
        self.assertEqual(
            {item.variant.variant_id for item in result.matches}, {"v-best", "v-cheap"}
        )
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "v-cheap")
        self.assertTrue(result.can_claim_catalogue_minimum)
        self.assertEqual(
            catalogue.lookup(ExactIdentifier(IdentifierKind.SKU, "SKU-BEST"))[
                0
            ].variant.variant_id,
            "v-best",
        )
        self.assertEqual(
            catalogue.lookup(ExactIdentifier(IdentifierKind.SKU, "sku-best")), ()
        )
        self.assertEqual(
            self.database.vocabulary()["category"]["backpacks"], "backpack"
        )

    def test_full_replace_and_stale_job_compare_and_set(self):
        self.publish()
        raw = fabricated_document("fixture-2", "fixture-1")
        raw["variants"] = raw["variants"][:1]
        raw["products"] = raw["products"][:1]
        self.publish(raw)
        with self.assertRaises(PublicationConflict):
            self.publish()
        state = self.database.inspect()
        self.assertEqual(state["variant_count"], 1)
        self.assertEqual(state["search_count"], 1)
        self.assertEqual(state["revision"], "fixture-2")

    def test_failed_publication_rolls_back_every_branch(self):
        self.publish()
        bundle = parse_import(fabricated_document("fixture-2", "fixture-1"))
        broken = replace(bundle, aliases={"invalid": object()})
        with self.assertRaises(TypeError):
            self.database.publish(broken)
        state = self.database.inspect()
        self.assertEqual(state["revision"], "fixture-1")
        self.assertEqual(state["product_count"], 3)
        self.assertEqual(state["search_count"], 3)

    def test_repeatable_read_does_not_mix_old_and_new_publication(self):
        self.publish()
        with self.database.connect() as reader:
            reader.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            old = self.database.snapshot_in(reader)
            self.publish(fabricated_document("fixture-2", "fixture-1"))
            after = self.database.snapshot_in(reader)
            self.assertEqual(old.state["revision"], after.state["revision"])
        self.assertEqual(self.database.snapshot().state["revision"], "fixture-2")

    def test_parallel_publishers_cannot_overwrite_each_other(self):
        def publish(revision):
            try:
                return self.publish(fabricated_document(revision))
            except PublicationConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(publish, ("writer-a", "writer-b")))
        self.assertEqual(results.count("conflict"), 1)
        self.assertIn(self.database.inspect()["revision"], ("writer-a", "writer-b"))

    def test_expired_source_and_unknown_prices_block_action_claims(self):
        self.publish()
        with self.database.connect() as connection:
            connection.execute("UPDATE catalogue_state SET valid_until='2000-01-01'")
        result = PostgresCatalogue(self.database).search(
            SearchRequest(HardConstraints("INR", category="backpack"))
        )
        self.assertEqual(result.matches, ())
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertFalse(result.can_claim_catalogue_minimum)

    def test_real_pgvector_lexical_price_roles_and_hard_constraints(self):
        self.publish(encoder=FixtureEncoder())
        catalogue = PostgresCatalogue(self.database, FixtureEncoder())
        request = SearchRequest(
            HardConstraints("INR", category="backpack", colour="black"),
            RetrievalRoute.DISCOVERY,
            semantic_query="college backpack",
        )
        result = catalogue.search(request)
        self.assertEqual(result.overall_match.variant.variant_id, "v-best")
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "v-cheap")
        self.assertNotIn(
            "v-accessory", {item.variant.variant_id for item in result.matches}
        )
        self.assertFalse(result.can_claim_catalogue_minimum)
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)

    def test_unconfigured_or_mismatched_semantics_is_not_silent_no_match(self):
        self.publish()
        request = SearchRequest(
            HardConstraints("INR", category="backpack"),
            RetrievalRoute.DISCOVERY,
            semantic_query="college backpack",
        )
        result = PostgresCatalogue(self.database, FixtureEncoder()).search(request)
        self.assertFalse(result.can_claim_no_match)
        self.assertTrue(any("generation" in issue.detail for issue in result.issues))

    def test_empty_import_can_only_assert_its_declared_source(self):
        raw = fabricated_document()
        raw["products"], raw["variants"] = [], []
        self.publish(raw)
        state = self.database.inspect()
        self.assertTrue(state["populated"])
        self.assertEqual(state["product_count"], 0)
        result = PostgresCatalogue(self.database).search(
            SearchRequest(HardConstraints("INR"))
        )
        self.assertTrue(result.can_claim_no_match)
        self.assertEqual(self.database.snapshot().catalogue.coverage, Coverage.COMPLETE)
