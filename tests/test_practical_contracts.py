"""Professor demonstrations of public contracts, using isolated authored fixtures."""

import unittest
from dataclasses import replace

from tests.fixtures import product, variant
from voicecart.application import money_text
from voicecart.catalogue import qualify
from voicecart.domain import (
    CatalogueItem,
    Eligibility,
    HardConstraints,
    Money,
    PriceLimit,
    PriceOperator,
)
from voicecart.nlu import InterpretationError, rupees_to_minor, whole_number


class PracticalContracts(unittest.TestCase):
    def test_price_equivalence_partitions_and_strict_inclusive_boundaries(self):
        for operator, expected in [
            (PriceOperator.LT, [True, False, False]),
            (PriceOperator.LTE, [True, True, False]),
        ]:
            limit = PriceLimit(Money(10000, "INR"), operator)
            for price, accepted in zip([9999, 10000, 10001], expected, strict=True):
                with self.subTest(operator=operator, price=price):
                    self.assertEqual(limit.permits(Money(price, "INR")), accepted)
        for price in [-1, 1.5, True]:
            with (
                self.subTest(invalid=price),
                self.assertRaises((ValueError, TypeError)),
            ):
                Money(price, "INR")
        item = CatalogueItem(product(), variant(price=None))
        self.assertIs(qualify(item, HardConstraints("INR")).state, Eligibility.UNKNOWN)

    def test_eligibility_decision_table_rejected_dominates_unknown(self):
        rows = [
            ({}, {}, Eligibility.QUALIFIED),
            ({"active": False}, {}, Eligibility.REJECTED),
            ({}, {"colour": "blue"}, Eligibility.REJECTED),
            ({}, {"price": 10001}, Eligibility.REJECTED),
            ({}, {"available": False}, Eligibility.REJECTED),
            ({}, {"available": None}, Eligibility.UNKNOWN),
            ({}, {"price": None}, Eligibility.UNKNOWN),
            ({"active": False}, {"price": None}, Eligibility.REJECTED),
        ]
        constraint = HardConstraints(
            "INR",
            colour="black",
            price_limit=PriceLimit(Money(10000, "INR"), PriceOperator.LTE),
        )
        for parent, offer, state in rows:
            with self.subTest(parent=parent, offer=offer):
                item = CatalogueItem(
                    product(**parent), variant(**{"price": 9999, **offer})
                )
                self.assertIs(qualify(item, constraint).state, state)
        # A known colour mismatch cannot become qualified due to a missing price.
        self.assertIs(
            qualify(
                CatalogueItem(product(), replace(variant(price=None), colour="blue")),
                constraint,
            ).state,
            Eligibility.REJECTED,
        )

    def test_money_text_three_feasible_return_paths(self):
        self.assertEqual(money_text(100, "INR"), "1 rupees")
        self.assertEqual(money_text(101, "INR"), "1 rupees and 1 paise")
        self.assertEqual(money_text(100, "USD"), "100 minor units USD")

    def test_amount_parser_and_number_loop_feasible_inputs(self):
        for text, expected in [
            ("0", 0),
            ("0.01", 1),
            ("1,00,000.50", 10000050),
            ("twenty one", 2100),
        ]:
            with self.subTest(text=text):
                self.assertEqual(rupees_to_minor(text), expected)
        for text in ["", "-1", "1.001", "NaN", "1,00", "x" * 101]:
            with (
                self.subTest(text=text),
                self.assertRaises((InterpretationError, ValueError)),
            ):
                rupees_to_minor(text)
        # Numeric fast path skips the word loop; empty words fail before iteration.
        for text, expected in [
            ("0", 0),
            ("one", 1),
            ("twenty one", 21),
            ("one hundred and five", 105),
            ("ninety nine lakh ninety nine thousand nine hundred ninety nine", 9999999),
        ]:
            self.assertEqual(whole_number(text), expected)
        for text in ["", "and one", "one one", "one thousand thousand", "one robot"]:
            with self.subTest(text=text), self.assertRaises(InterpretationError):
                whole_number(text)
