from app.models import Order, OrderItem
from app.orders import build_receipt


def _cart():
    """2 lattes and 1 blueberry muffin — subtotal 12.50."""
    return [
        OrderItem(name="latte", quantity=2),
        OrderItem(name="blueberry muffin", quantity=1),
    ]


def test_non_member_total():
    receipt = build_receipt(Order(items=_cart(), loyalty_member=False))
    assert receipt.subtotal == 12.50
    assert receipt.discount == 0.0
    assert receipt.tax == 1.00
    assert receipt.total == 13.50


def test_loyalty_member_total():
    receipt = build_receipt(Order(items=_cart(), loyalty_member=True))
    assert receipt.subtotal == 12.50
    assert receipt.discount == 1.25
    assert receipt.tax == 0.90
    assert receipt.total == 12.15
