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
