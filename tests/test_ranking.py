import unittest

from tests.fixtures import product, request, variant
from voicecart.catalogue import InMemoryCatalogue
from voicecart.domain import Coverage
from voicecart.ranking import RankingContractError


class FixtureOrder:
    """Test judgments only; no production weights or automatic relevance claim."""

    def __init__(self, order, version="fixture-judgments-v1"):
        self.order = order
        self.version = version
        self.seen = ()

    def rank(self, request, qualified):
        self.seen = tuple(item.variant.variant_id for item in qualified)
        return self.order


class RankingBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.db = InMemoryCatalogue(
            [product(), product("accessory", category="bag_accessory")],
            [
                variant("cheap", price=90_000),
                variant("better-fit", price=150_000),
                variant("wrong-colour", price=500, colour="blue"),
                variant("accessory", "accessory", price=100),
                variant("unknown-price", price=None),
            ],
            revision="fixture-ranking-snapshot",
            coverage=Coverage.COMPLETE,
        )

    def test_overall_ranked_match_is_distinct_from_cheapest_match(self):
        policy = FixtureOrder(("better-fit", "cheap"))
        result = self.db.search(request(), ranking_policy=policy)
        self.assertEqual(result.overall_match.variant.variant_id, "better-fit")
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "cheap")
        self.assertEqual(result.ranking_policy_version, "fixture-judgments-v1")
        # A missing potentially qualifying price still blocks a global claim,
        # regardless of how attractive the ranked results look.
        self.assertFalse(result.can_claim_catalogue_minimum)

    def test_only_hard_qualified_records_reach_ranking(self):
        policy = FixtureOrder(("better-fit", "cheap"))
        self.db.search(request(), ranking_policy=policy)
        self.assertEqual(set(policy.seen), {"cheap", "better-fit"})

    def test_absent_ranking_policy_does_not_invent_overall_relevance(self):
        result = self.db.search(request())
        self.assertIsNone(result.overall_match)
        self.assertIsNone(result.ranking_policy_version)
        self.assertEqual(result.ranked_matches, ())
        self.assertEqual(result.cheapest_qualifying_match.variant.variant_id, "cheap")

    def test_ranking_order_cannot_change_the_price_minimum(self):
        first = self.db.search(
            request(), ranking_policy=FixtureOrder(("better-fit", "cheap"))
        )
        second = self.db.search(
            request(), ranking_policy=FixtureOrder(("cheap", "better-fit"), "v2")
        )
        self.assertEqual(
            first.cheapest_qualifying_match, second.cheapest_qualifying_match
        )
        self.assertNotEqual(first.overall_match, second.overall_match)

    def test_policy_cannot_inject_unqualified_ids_drop_or_duplicate_matches(self):
        for order in (
            ("wrong-colour", "cheap"),
            ("accessory", "cheap"),
            ("unknown-price", "cheap"),
            ("cheap", "cheap"),
            ("better-fit",),
            ("better-fit", "cheap", "new-id"),
        ):
            with self.subTest(order=order), self.assertRaises(RankingContractError):
                self.db.search(request(), ranking_policy=FixtureOrder(order))

    def test_unversioned_and_untyped_policy_outputs_are_rejected(self):
        for policy in (
            FixtureOrder(("better-fit", "cheap"), version=""),
            FixtureOrder(("better-fit", "cheap"), version=None),
            FixtureOrder(["better-fit", "cheap"]),
            FixtureOrder(([], "cheap")),
        ):
            with self.subTest(policy=policy), self.assertRaises(RankingContractError):
                self.db.search(request(), ranking_policy=policy)


if __name__ == "__main__":
    unittest.main()
