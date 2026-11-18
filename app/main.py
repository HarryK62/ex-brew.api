"""brew-api — the Maple & Main Coffee ordering backend."""
from fastapi import FastAPI, HTTPException

from app.menu import MENU, get_item
from app.models import Order, OrderItem, QuoteRequest, QuoteResponse, QuoteSavings, Receipt
from app.orders import build_receipt

app = FastAPI(title="brew-api", description="Maple & Main Coffee ordering backend")


@app.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/menu")
def menu() -> dict:
    """Return the full menu."""
    return {"items": [item.model_dump() for item in MENU.values()]}


def _check_items(items: list[OrderItem]) -> None:
    """Reject a cart with anything not on the menu.

    get_item (via build_receipt) raises KeyError for unknown items; turn that
    into a 400 so a bad cart doesn't 500.
    """
    try:
        for entry in items:
            get_item(entry.name)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown menu item: {exc.args[0]}")


@app.post("/orders", response_model=Receipt)
def create_order(order: Order) -> Receipt:
    """Price a cart and return its receipt."""
    _check_items(order.items)
    return build_receipt(order)


@app.post("/quote", response_model=QuoteResponse)
def quote(request: QuoteRequest) -> QuoteResponse:
    """Show how much loyalty saves on a cart.

    Prices the cart twice with build_receipt (as a non-member and as a
    member) so the quote always matches what /orders would charge. Savings
    are differences of the two rounded receipts, never subtotal * rate.
    """
    _check_items(request.items)
    standard = build_receipt(Order(items=request.items, loyalty_member=False))
    member = build_receipt(Order(items=request.items, loyalty_member=True))
    savings = QuoteSavings(
        discount=member.discount,
        tax=round(standard.tax - member.tax, 2),
        total=round(standard.total - member.total, 2),
    )
    return QuoteResponse(standard=standard, member=member, savings=savings)
