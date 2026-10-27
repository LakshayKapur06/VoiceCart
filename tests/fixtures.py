"""Explicit fixture assertions, not imported merchant facts or a ranking policy."""

from voicecart.domain import (
    Freshness,
    HardConstraints,
    Money,
    PriceLimit,
    PriceOperator,
    Product,
    ProductId,
    SearchRequest,
    Variant,
    VariantId,
)


def product(identifier="p1", **changes):
    fields = dict(
        product_id=ProductId(identifier), name="Backpack", category="backpack"
    )
    fields.update(changes)
    return Product(**fields)


def variant(identifier="v1", parent="p1", price=100_000, **changes):
    fields = dict(
        variant_id=VariantId(identifier),
        product_id=ProductId(parent),
        price=(
            price
            if isinstance(price, Money)
            else Money(price, "INR")
            if price is not None
            else None
        ),
        colour="black",
        size="medium",
        available=True,
        stock_quantity=5,
        price_freshness=Freshness.CURRENT,
    )
    fields.update(changes)
    return Variant(**fields)


def request(limit=200_000, operator=PriceOperator.LT, **constraints):
    fields = dict(
        currency="INR",
        category="backpack",
        colour="black",
        price_limit=PriceLimit(Money(limit, "INR"), operator),
    )
    fields.update(constraints)
    return SearchRequest(HardConstraints(**fields))
