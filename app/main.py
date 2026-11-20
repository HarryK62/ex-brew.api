"""brew-api — the Maple & Main Coffee ordering backend."""
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.menu import MENU, get_item
from app.models import MenuEntry, Order, OrderItem, QuoteRequest, QuoteResponse, QuoteSavings, Receipt
from app.orders import build_receipt
from app.promos import PromoNotActive, promo_rate

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
    top and the purchase price a non-member pays for one. The tax comes from
    build_receipt, so the menu can never disagree with what /orders charges.
    """
    entries = []
    for item in MENU.values():
        receipt = build_receipt(Order(items=[OrderItem(name=item.name)]))
        entries.append(
            MenuEntry(name=item.name, price=item.price, tax=receipt.tax,
                      purchase_price=receipt.total)
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
    """Reject an unknown, expired or not-yet-started code with a 400, never ignore it."""
    try:
        promo_rate(code)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown promo code: {exc.args[0]}")
    except PromoNotActive as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def _price(order: Order) -> Receipt:
    """build_receipt, with a code that expires mid-request turned into a 400.

    _check_promo runs first, but the date can roll past midnight before
    build_receipt checks the code again; without this that would be a 500.
    """
    try:
        return build_receipt(order)
    except PromoNotActive as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/orders", response_model=Receipt)
def create_order(order: Order) -> Receipt:
    """Price a cart and return its receipt."""
    _check_items(order.items)
    _check_promo(order.promo_code)
    return _price(order)


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
    standard = _price(Order(items=request.items, loyalty_member=False,
                                   promo_code=request.promo_code))
    member = _price(Order(items=request.items, loyalty_member=True,
                                 promo_code=request.promo_code))
    savings = QuoteSavings(
        discount=member.discount,
        tax=round(standard.tax - member.tax, 2),
        total=round(standard.total - member.total, 2),
    )
    return QuoteResponse(standard=standard, member=member, savings=savings)
