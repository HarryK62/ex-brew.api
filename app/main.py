"""brew-api — the Maple & Main Coffee ordering backend."""
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.menu import MENU, get_item
from app.models import Order, Receipt
from app.orders import build_receipt

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
    """Return the full menu."""
    return {"items": [item.model_dump() for item in MENU.values()]}


@app.post("/orders", response_model=Receipt)
def create_order(order: Order) -> Receipt:
    """Price a cart and return its receipt."""
    try:
        # get_item (via build_receipt) raises KeyError for anything not on the menu
        for entry in order.items:
            get_item(entry.name)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown menu item: {exc.args[0]}")
    return build_receipt(order)
