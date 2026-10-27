import itertools
import random
import unittest
from dataclasses import replace

from tests.fixtures import product, request, variant
from voicecart.catalogue import InMemoryCatalogue, qualify
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
    Money,
    PriceOperator,
    RetrievalRoute,
    SearchRequest,
    SearchStatus,
)


def catalogue(variants, products=None, coverage=Coverage.COMPLETE):
    return InMemoryCatalogue(
        [product()] if products is None else products,
        variants,
        revision="synthetic-snapshot-v1",
        coverage=coverage,
    )


def ids(items):
    return tuple(item.variant.variant_id for item in items)


class StructuredSelectionTests(unittest.TestCase):
    def test_full_catalogue_finds_cheaper_poorly_described_item_beyond_top_k(self):
        products = [
            product(
                "p-top1", description="Black backpack for college with laptop space"
            ),
            product("p-top2", description="Popular black backpack, college daily bag"),
            product("p-omitted", name="R7", description=""),
        ]
        variants = [
            variant("v-top1", "p-top1", 120_000),
            variant("v-top2", "p-top2", 150_000),
            variant("v-omitted", "p-omitted", 90_000),
        ]
        hypothetical_semantic_top_k = variants[:2]
        self.assertEqual(
            min(v.price.minor_units for v in hypothetical_semantic_top_k), 120_000
        )
        result = catalogue(variants, products).search(request())
        self.assertEqual(
            result.cheapest_qualifying_match.variant.variant_id, "v-omitted"
        )
        self.assertEqual(set(ids(result.matches)), {"v-top1", "v-top2", "v-omitted"})
        self.assertTrue(result.can_claim_catalogue_minimum)
        self.assertEqual(result.catalogue_revision, "synthetic-snapshot-v1")

    def test_strict_and_inclusive_price_boundaries(self):
        db = catalogue([variant("at", price=200_000), variant("over", price=200_001)])
        strict = db.search(request(operator=PriceOperator.LT))
        inclusive = db.search(request(operator=PriceOperator.LTE))
        self.assertEqual(strict.status, SearchStatus.NO_MATCH)
        self.assertTrue(strict.can_claim_no_match)
        self.assertEqual(ids(inclusive.matches), ("at",))
        self.assertTrue(inclusive.can_claim_catalogue_minimum)

    def test_paise_boundary_uses_integers_without_rounding(self):
        db = catalogue([variant("below", price=199_999), variant("at", price=200_000)])
        self.assertEqual(ids(db.search(request()).matches), ("below",))

    def test_missing_price_is_unknown_and_blocks_global_claim(self):
        result = catalogue([variant("known"), variant("missing", price=None)]).search(
            request()
        )
        self.assertEqual(ids(result.matches), ("known",))
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertEqual(result.scope, ClaimScope.VERIFIED_RECORDS)
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "known")
        self.assertFalse(result.can_claim_catalogue_minimum)
        self.assertIn(IssueCode.MISSING_PRICE, {issue.code for issue in result.issues})

    def test_only_missing_price_is_not_a_verified_no_match(self):
        result = catalogue([variant(price=None)]).search(request())
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertIsNone(result.cheapest_qualifying_match)
        self.assertFalse(result.can_claim_no_match)

    def test_unknown_required_category_colour_or_size_never_matches(self):
        for missing in ("category", "colour", "size"):
            with self.subTest(missing=missing):
                parent = product(category=None) if missing == "category" else product()
                item = (
                    variant(**{missing: None}) if missing != "category" else variant()
                )
                result = catalogue([item], [parent]).search(request(size="medium"))
                self.assertEqual(result.matches, ())
                self.assertEqual(result.status, SearchStatus.INCOMPLETE)
                self.assertFalse(result.can_claim_no_match)
                self.assertIn(
                    IssueCode.UNKNOWN_ATTRIBUTE, {i.code for i in result.issues}
                )

    def test_unknown_unrequested_size_does_not_block_selection(self):
        result = catalogue([variant(size=None)]).search(request())
        self.assertTrue(result.can_claim_catalogue_minimum)

    def test_known_nonmatch_dominates_unrelated_unknown_facts(self):
        db = catalogue(
            [variant("backpack"), variant("shirt", "p-shirt", price=None, colour=None)],
            [product(), product("p-shirt", category="shirt")],
        )
        result = db.search(request())
        self.assertEqual(ids(result.matches), ("backpack",))
        self.assertTrue(result.can_claim_catalogue_minimum)
        self.assertEqual(result.issues, ())

    def test_wrong_colour_dominates_unknown_category(self):
        item = CatalogueItem(product(category=None), variant(colour="blue", price=None))
        self.assertIs(qualify(item, request().constraints).state, Eligibility.REJECTED)

    def test_description_cannot_fill_a_missing_structured_colour(self):
        db = catalogue(
            [variant(colour=None)], [product(description="solid black backpack")]
        )
        self.assertEqual(db.search(request()).status, SearchStatus.INCOMPLETE)

    def test_stale_and_unverified_prices_are_not_qualified(self):
        for freshness in (Freshness.STALE, Freshness.UNKNOWN):
            with self.subTest(freshness=freshness):
                result = catalogue([variant(price_freshness=freshness)]).search(
                    request()
                )
                self.assertEqual(result.status, SearchStatus.INCOMPLETE)
                self.assertIsNone(result.cheapest_qualifying_match)
                self.assertFalse(result.can_claim_no_match)

    def test_stale_above_budget_price_cannot_prove_nonmatch(self):
        result = catalogue(
            [variant(price=900_000, price_freshness=Freshness.STALE)]
        ).search(request())
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertFalse(result.can_claim_no_match)

    def test_variant_identity_does_not_borrow_other_colour_price_or_stock(self):
        db = catalogue(
            [
                variant(
                    "black-small",
                    price=150_000,
                    size="small",
                    stock_quantity=0,
                    available=False,
                ),
                variant("blue-small", price=1_000, colour="blue", size="small"),
                variant("black-large", price=170_000, size="large"),
            ]
        )
        small = db.search(request(size="small"))
        self.assertTrue(small.can_claim_no_match)
        any_size = db.search(request())
        self.assertEqual(ids(any_size.matches), ("black-large",))
        self.assertEqual(
            any_size.cheapest_qualifying_match.variant.price.minor_units, 170_000
        )

    def test_price_ties_are_stable_for_every_input_permutation(self):
        variants = [variant("b"), variant("a"), variant("c", price=120_000)]
        for permutation in itertools.permutations(variants):
            result = catalogue(permutation).search(request())
            self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "a")
            self.assertEqual(ids(result.matches), ("a", "b", "c"))

    def test_empty_complete_catalogue_proves_no_match_but_not_a_minimum(self):
        result = catalogue([], []).search(request())
        self.assertEqual(result.status, SearchStatus.NO_MATCH)
        self.assertTrue(result.can_claim_no_match)
        self.assertFalse(result.can_claim_catalogue_minimum)

    def test_all_verified_nonmatches_prove_no_match(self):
        result = catalogue(
            [variant(colour="red"), variant("costly", price=300_000)]
        ).search(request())
        self.assertEqual(result.matches, ())
        self.assertTrue(result.can_claim_no_match)

    def test_partial_and_unknown_coverage_block_global_claims(self):
        for coverage in (Coverage.PARTIAL, Coverage.UNKNOWN):
            for items in ([], [variant()]):
                with self.subTest(coverage=coverage, items=len(items)):
                    result = catalogue(items, coverage=coverage).search(request())
                    self.assertEqual(result.status, SearchStatus.INCOMPLETE)
                    self.assertFalse(result.can_claim_catalogue_minimum)
                    self.assertFalse(result.can_claim_no_match)

    def test_coverage_defaults_to_unknown_even_for_well_formed_records(self):
        result = InMemoryCatalogue([product()], [variant()], revision="v1").search(
            request()
        )
        self.assertEqual(result.status, SearchStatus.INCOMPLETE)
        self.assertIn(IssueCode.UNKNOWN_COVERAGE, {i.code for i in result.issues})

    def test_currencies_are_not_compared_or_converted(self):
        db = catalogue([variant("usd", price=Money(1, "USD")), variant("inr")])
        result = db.search(request())
        self.assertEqual(ids(result.matches), ("inr",))
        self.assertTrue(result.can_claim_catalogue_minimum)

    def test_known_zero_price_is_a_valid_minimum(self):
        result = catalogue([variant("paid"), variant("free", price=0)]).search(
            request()
        )
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "free")

    def test_unknown_availability_and_multi_unit_stock_block_claims(self):
        for item in (variant(available=None), variant(stock_quantity=None)):
            with self.subTest(item=item):
                result = catalogue([item]).search(request(quantity=2))
                self.assertEqual(result.status, SearchStatus.INCOMPLETE)
                self.assertFalse(result.can_claim_no_match)
        # An explicit available flag asserts at least one, not an invented count.
        single = catalogue([variant(stock_quantity=None)]).search(request(quantity=1))
        self.assertTrue(single.can_claim_catalogue_minimum)

    def test_insufficient_known_stock_and_inactive_records_are_excluded(self):
        db = catalogue(
            [variant("one", stock_quantity=1), variant("inactive", active=False)]
        )
        self.assertTrue(db.search(request(quantity=2)).can_claim_no_match)
        parent_inactive = catalogue([variant()], [product(active=False)])
        self.assertTrue(parent_inactive.search(request()).can_claim_no_match)

    def test_snapshot_does_not_change_when_input_lists_change(self):
        source = [variant("original")]
        db = catalogue(source)
        source.append(variant("new", price=1))
        self.assertEqual(
            db.search(request()).cheapest_qualifying_match.variant.variant_id,
            "original",
        )

    def test_discovery_is_explicitly_unsupported_not_structured_fallback(self):
        query = SearchRequest(
            HardConstraints("INR"),
            route=RetrievalRoute.DISCOVERY,
            semantic_query="good for college",
        )
        result = catalogue([variant()]).search(query)
        self.assertEqual(result.status, SearchStatus.UNSUPPORTED)
        self.assertEqual(result.scope, ClaimScope.UNVERIFIED)
        self.assertEqual(result.matches, ())
        self.assertFalse(result.can_claim_no_match)

    def test_generated_complete_catalogues_agree_with_independent_full_set_oracle(self):
        rng = random.Random(173)
        for trial in range(25):
            parents = [
                product(f"p{i}", category=rng.choice(["backpack", "shirt"]))
                for i in range(40)
            ]
            variants = [
                variant(
                    f"v{i:03}",
                    parent.product_id,
                    rng.randrange(0, 300_001),
                    colour=rng.choice(["black", "blue"]),
                    available=rng.choice([True, False]),
                )
                for i, parent in enumerate(parents)
            ]
            category = {p.product_id: p.category for p in parents}
            for operator in (PriceOperator.LT, PriceOperator.LTE):
                bound = 200_000
                # Independent oracle reads EVERY original fixture row, not qualify()
                # or a retrieved candidate list. All prices/facts are asserted current.
                expected = sorted(
                    (v.price.minor_units, v.variant_id)
                    for v in variants
                    if category[v.product_id] == "backpack"
                    and v.colour == "black"
                    and v.available is True
                    and (
                        v.price.minor_units < bound
                        or (
                            operator is PriceOperator.LTE
                            and v.price.minor_units == bound
                        )
                    )
                )
                rng.shuffle(variants)
                with self.subTest(trial=trial, operator=operator):
                    result = catalogue(variants, parents).search(
                        request(operator=operator)
                    )
                    actual = result.cheapest_qualifying_match
                    pair = (
                        (actual.variant.price.minor_units, actual.variant.variant_id)
                        if actual
                        else None
                    )
                    self.assertEqual(pair, expected[0] if expected else None)
                    self.assertEqual(
                        set(ids(result.matches)), {key for _, key in expected}
                    )
                    self.assertEqual(result.can_claim_no_match, not expected)


class ExactLookupAndSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.db = catalogue(
            [
                variant("black", sku="SKU-BLK"),
                variant("blue", colour="blue", sku="SKU-BLU"),
            ],
            [product(model_number="MODEL-X")],
        )

    def test_exact_lookup_resolves_each_supported_identifier_kind(self):
        cases = (
            (IdentifierKind.VARIANT_ID, "black", ("black",)),
            (IdentifierKind.SKU, "SKU-BLU", ("blue",)),
            (IdentifierKind.PRODUCT_ID, "p1", ("black", "blue")),
            (IdentifierKind.MODEL_NUMBER, "MODEL-X", ("black", "blue")),
        )
        for kind, value, expected in cases:
            with self.subTest(kind=kind):
                self.assertEqual(
                    ids(self.db.lookup(ExactIdentifier(kind, value))), expected
                )

    def test_lookup_is_case_sensitive_and_does_not_fuzzily_substitute(self):
        self.assertEqual(
            self.db.lookup(ExactIdentifier(IdentifierKind.SKU, "sku-blk")), ()
        )
        self.assertEqual(
            self.db.lookup(ExactIdentifier(IdentifierKind.MODEL_NUMBER, "MODEL")), ()
        )

    def test_exact_search_still_enforces_constraints_and_scopes_identity(self):
        exact = replace(
            request(),
            route=RetrievalRoute.EXACT,
            identifier=ExactIdentifier(IdentifierKind.VARIANT_ID, "blue"),
        )
        self.assertEqual(self.db.search(exact).status, SearchStatus.NO_MATCH)
        black = replace(
            exact, identifier=ExactIdentifier(IdentifierKind.VARIANT_ID, "black")
        )
        result = self.db.search(black)
        self.assertEqual(result.scope, ClaimScope.EXACT_IDENTIFIER)
        self.assertFalse(result.can_claim_catalogue_minimum)
        self.assertEqual(ids(result.matches), ("black",))

    def test_unknown_identifier_in_complete_and_incomplete_sources(self):
        exact = replace(
            request(),
            route=RetrievalRoute.EXACT,
            identifier=ExactIdentifier(IdentifierKind.SKU, "missing"),
        )
        self.assertTrue(self.db.search(exact).can_claim_no_match)
        partial = catalogue([variant()], coverage=Coverage.PARTIAL)
        self.assertEqual(partial.search(exact).status, SearchStatus.INCOMPLETE)

    def test_raw_lookup_does_not_assert_availability(self):
        db = catalogue([variant(available=False)])
        identifier = ExactIdentifier(IdentifierKind.VARIANT_ID, "v1")
        self.assertEqual(ids(db.lookup(identifier)), ("v1",))
        exact = replace(request(), route=RetrievalRoute.EXACT, identifier=identifier)
        self.assertTrue(db.search(exact).can_claim_no_match)

    def test_duplicate_ids_skus_and_orphan_variants_fail_snapshot_creation(self):
        with self.assertRaises(ValueError):
            catalogue([variant()], [product(), product()])
        for items in (
            [variant(), variant()],
            [variant("a", sku="same"), variant("b", sku="same")],
            [variant(parent="missing-parent")],
        ):
            with self.subTest(items=items), self.assertRaises(ValueError):
                catalogue(items)

    def test_untyped_coverage_and_invalid_records_fail_instead_of_being_dropped(self):
        with self.assertRaises(TypeError):
            catalogue([variant()], coverage=True)
        with self.assertRaises(TypeError):
            catalogue([{"variant_id": "not-a-validated-record"}])


if __name__ == "__main__":
    unittest.main()
