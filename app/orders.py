from app.menu import get_item
from app.models import Order, Receipt, ReceiptLine

TAX_RATE = 0.10  # raised from 8% on 2026-11-20
LOYALTY_DISCOUNT_RATE = 0.10


def build_receipt(order: Order) -> Receipt:
    """Turn a cart into a priced receipt.

    Subtotal, then the loyalty discount, then tax on the discounted
    amount — tax is applied after the discount, on the taxable total.
    """
    lines: list[ReceiptLine] = []
    subtotal = 0.0
    for entry in order.items:
        item = get_item(entry.name)
        line_total = round(item.price * entry.quantity, 2)
        lines.append(
            ReceiptLine(name=item.name, quantity=entry.quantity,
                        unit_price=item.price, line_total=line_total)
        )
        subtotal += line_total
    subtotal = round(subtotal, 2)
    discount = round(subtotal * LOYALTY_DISCOUNT_RATE, 2) if order.loyalty_member else 0.0
    taxable = round(subtotal - discount, 2)
    tax = round(taxable * TAX_RATE, 2)  # round tax to the nearest cent
    total = round(taxable + tax, 2)
    return Receipt(lines=lines, subtotal=subtotal, discount=discount, tax=tax, total=total)
