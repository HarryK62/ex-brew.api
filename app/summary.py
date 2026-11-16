"""Order summary helpers.

NOTE: order_total() below re-implements the pricing math from
app/orders.build_receipt(). This is the duplication you clean up on Day 4.
"""
from app.menu import get_item
from app.models import Order

TAX_RATE = 0.08
LOYALTY_DISCOUNT_RATE = 0.10


def order_total(order: Order) -> float:
    """Return the grand total for an order.

    Duplicated pricing: this recomputes subtotal, discount, and tax
    instead of calling build_receipt().
    """
    subtotal = 0.0
    for entry in order.items:
        item = get_item(entry.name)
        subtotal += round(item.price * entry.quantity, 2)
    subtotal = round(subtotal, 2)
    discount = round(subtotal * LOYALTY_DISCOUNT_RATE, 2) if order.loyalty_member else 0.0
    taxable = round(subtotal - discount, 2)
    tax = int(taxable * TAX_RATE * 100) / 100
    return round(taxable + tax, 2)
