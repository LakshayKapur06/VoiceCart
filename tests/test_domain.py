import unittest
from dataclasses import FrozenInstanceError

from tests.fixtures import product, variant
from voicecart.domain import (
    MAX_MINOR_UNITS,
    CatalogueItem,
    ExactIdentifier,
    Freshness,
    HardConstraints,
    IdentifierKind,
    Money,
    PriceLimit,
    PriceOperator,
    RetrievalRoute,
    SearchRequest,
)


class MoneyAndContractTests(unittest.TestCase):
    def test_money_rejects_float_bool_and_string(self):
        for value in (1999.99, True, False, "200000", None):
            with self.subTest(value=value), self.assertRaises(TypeError):
                Money(value, "INR")

    def test_money_is_nonnegative_bounded_integer(self):
        self.assertEqual(Money(0, "INR").minor_units, 0)
        self.assertEqual(Money(MAX_MINOR_UNITS, "INR").minor_units, MAX_MINOR_UNITS)
        for value in (-1, MAX_MINOR_UNITS + 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Money(value, "INR")

    def test_currency_is_explicit_and_not_silently_normalized(self):
        for currency in (None, "", "inr", "IN", "123", " INR"):
            with self.subTest(currency=currency), self.assertRaises(ValueError):
                Money(1, currency)

    def test_price_operators_have_different_boundary_semantics(self):
        amount = Money(200_000, "INR")
        self.assertFalse(PriceLimit(amount, PriceOperator.LT).permits(amount))
        self.assertTrue(PriceLimit(amount, PriceOperator.LTE).permits(amount))
        self.assertFalse(PriceLimit(amount, PriceOperator.LTE).permits(Money(1, "USD")))

    def test_untyped_operator_or_money_is_rejected(self):
        with self.assertRaises(TypeError):
            PriceLimit(Money(200_000, "INR"), "lte")
        with self.assertRaises(TypeError):
            PriceLimit(200_000, PriceOperator.LT)

    def test_conflicting_budget_currency_is_rejected(self):
        with self.assertRaises(ValueError):
            HardConstraints(
                currency="INR",
                price_limit=PriceLimit(Money(10, "USD"), PriceOperator.LT),
            )

    def test_quantity_must_be_positive_integer(self):
        for value in (0, -1, True, 1.5, "2"):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                HardConstraints("INR", quantity=value)

    def test_unknowns_stay_explicit_and_default_freshness_is_unknown(self):
        item = variant(price=None, colour=None, available=None)
        self.assertIsNone(item.price)
        self.assertIsNone(item.colour)
        self.assertIsNone(item.available)
        self.assertIs(
            type(item)(item.variant_id, item.product_id).price_freshness,
            Freshness.UNKNOWN,
        )

    def test_identity_attributes_and_boolean_fields_are_validated(self):
        for fields in (
            {"variant_id": ""},
            {"colour": "  "},
            {"available": 1},
            {"active": "yes"},
            {"stock_quantity": True},
            {"stock_quantity": -1},
            {"price": 20.5},
            {"price_freshness": "current"},
        ):
            with (
                self.subTest(fields=fields),
                self.assertRaises((TypeError, ValueError)),
            ):
                variant(**fields)
        with self.assertRaises(ValueError):
            product(name="")

    def test_zero_stock_cannot_be_asserted_available(self):
        with self.assertRaises(ValueError):
            variant(stock_quantity=0, available=True)

    def test_contracts_are_immutable(self):
        item = variant()
        with self.assertRaises(FrozenInstanceError):
            item.price = Money(1, "INR")

    def test_variant_cannot_be_joined_to_wrong_parent(self):
        with self.assertRaises(ValueError):
            CatalogueItem(product("other"), variant())

    def test_exact_route_requires_typed_identifier(self):
        with self.assertRaises(ValueError):
            SearchRequest(HardConstraints("INR"), route=RetrievalRoute.EXACT)
        with self.assertRaises(TypeError):
            ExactIdentifier("sku", "SKU-1")
        with self.assertRaises(ValueError):
            ExactIdentifier(IdentifierKind.SKU, " ")

    def test_route_mismatch_and_unsupported_fields_fail_explicitly(self):
        with self.assertRaises(ValueError):
            SearchRequest(
                HardConstraints("INR"),
                identifier=ExactIdentifier(IdentifierKind.SKU, "SKU-1"),
            )
        with self.assertRaises(TypeError):
            HardConstraints("INR", waterproof=True)
        with self.assertRaises(TypeError):
            SearchRequest(HardConstraints("INR"), route="discovery")

    def test_descriptive_text_cannot_be_silently_treated_as_structured(self):
        with self.assertRaises(ValueError):
            SearchRequest(HardConstraints("INR"), semantic_query="good for college")
        with self.assertRaises(TypeError):
            SearchRequest(HardConstraints("INR"), route=RetrievalRoute.DISCOVERY)


if __name__ == "__main__":
    unittest.main()
