# Day 2 · the failing test
#
# A customer reported that a loyalty order rang up a penny short, and a
# teammate added this test to reproduce it. Copy this file into tests/ to
# start Day 2:
#
#     tests/test_loyalty_rounding.py
#
# Then run `pytest -q` — you should see 4 passed, 1 failed.

from app.models import Order, OrderItem
from app.orders import build_receipt


def test_loyalty_receipt_rounds_tax():
    """A loyalty order of 1 latte + 1 cappuccino should total 8.50."""
    order = Order(
        items=[
            OrderItem(name="latte", quantity=1),
            OrderItem(name="cappuccino", quantity=1),
        ],
        loyalty_member=True,
    )
    receipt = build_receipt(order)
    assert receipt.tax == 0.63
    assert receipt.total == 8.50
