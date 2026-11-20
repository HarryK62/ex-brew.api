from app.models import Order, OrderItem
from app.orders import build_receipt
from app.summary import order_total


def test_order_total_matches_receipt():
    """order_total() must agree with build_receipt().total."""
    order = Order(
        items=[
            OrderItem(name="latte", quantity=2),
            OrderItem(name="blueberry muffin", quantity=1),
        ],
        loyalty_member=True,
    )
    assert order_total(order) == build_receipt(order).total == 12.15


import pytest


@pytest.mark.parametrize(
    "items, loyalty",
    [
        ([OrderItem(name="latte", quantity=2), OrderItem(name="blueberry muffin", quantity=1)], False),
        ([OrderItem(name="latte", quantity=1), OrderItem(name="cappuccino", quantity=1)], True),
        ([], True),
    ],
    ids=["non-member", "rounding-cart", "empty"],
)
def test_order_total_agrees_with_receipt(items, loyalty):
    order = Order(items=items, loyalty_member=loyalty)
    assert order_total(order) == build_receipt(order).total


def test_order_total_unknown_item_raises_keyerror():
    with pytest.raises(KeyError):
        order_total(Order(items=[OrderItem(name="mocha", quantity=1)]))
