"""Order summary helpers."""
from app.models import Order
from app.orders import build_receipt


def order_total(order: Order) -> float:
    """Return the grand total for an order.

    Delegates to build_receipt() so there is a single source of pricing.
    """
    return build_receipt(order).total
