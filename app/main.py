"""brew-api — the Maple & Main Coffee ordering backend."""
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.menu import MENU, get_item
from app.models import MenuEntry, Order, OrderItem, QuoteRequest, QuoteResponse, QuoteSavings, Receipt
from app.orders import TAX_RATE, build_receipt
from app.promos import promo_rate

# Load settings such as BREW_API_KEY from a local .env file, if there is one.
# .env is gitignored; see .env.example for the expected variables.
load_dotenv()

app = FastAPI(title="brew-api", description="Maple & Main Coffee ordering backend")


@app.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/menu")
def menu() -> dict:
    """Return the full menu with the tax shown for each item.

    Menu prices are pre-tax. Each entry shows the price, the tax added on
    top (rounded to the cent, as build_receipt does) and the purchase price
    a non-member pays for one.
    """
    entries = []
    for item in MENU.values():
        tax = round(item.price * TAX_RATE, 2)
        entries.append(
            MenuEntry(name=item.name, price=item.price, tax=tax,
                      purchase_price=round(item.price + tax, 2))
        )
    return {"items": [entry.model_dump() for entry in entries]}


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


def _check_promo(code: str | None) -> None:
    """Reject an unknown promo code with a 400 rather than silently ignoring it."""
    try:
        promo_rate(code)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown promo code: {exc.args[0]}")


@app.post("/orders", response_model=Receipt)
def create_order(order: Order) -> Receipt:
    """Price a cart and return its receipt."""
    _check_items(order.items)
    _check_promo(order.promo_code)
    return build_receipt(order)


@app.post("/quote", response_model=QuoteResponse)
def quote(request: QuoteRequest) -> QuoteResponse:
    """Show how much loyalty saves on a cart.

    Prices the cart twice with build_receipt (as a non-member and as a
    member) so the quote always matches what /orders would charge. Savings
    are differences of the two rounded receipts, never subtotal * rate.
    A promo code applies to both receipts, so savings stay loyalty-only.
    """
    _check_items(request.items)
    _check_promo(request.promo_code)
    standard = build_receipt(Order(items=request.items, loyalty_member=False,
                                   promo_code=request.promo_code))
    member = build_receipt(Order(items=request.items, loyalty_member=True,
                                 promo_code=request.promo_code))
    savings = QuoteSavings(
        discount=member.discount,
        tax=round(standard.tax - member.tax, 2),
        total=round(standard.total - member.total, 2),
    )
    return QuoteResponse(standard=standard, member=member, savings=savings)
