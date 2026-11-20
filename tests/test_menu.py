import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.menu import MENU, get_item
from app.models import Item, Order, OrderItem
from app.orders import build_receipt

client = TestClient(app)

EXPECTED_PRICES = {
    "latte": 4.82,
    "cappuccino": 4.55,
    "espresso": 3.21,
    "americano": 4.01,
    "blueberry muffin": 3.75,
    "croissant": 3.48,
}

# Henry's menu columns: Item, Price, Tax added, Purchase price (10% tax on top).
EXPECTED_MENU = [
    ("latte", 4.82, 0.48, 5.30),
    ("cappuccino", 4.55, 0.46, 5.01),
    ("espresso", 3.21, 0.32, 3.53),
    ("americano", 4.01, 0.40, 4.41),
    ("blueberry muffin", 3.75, 0.38, 4.13),
    ("croissant", 3.48, 0.35, 3.83),
]


def test_menu_has_expected_items_and_prices():
    assert {key: item.price for key, item in MENU.items()} == EXPECTED_PRICES


def test_menu_keys_match_lowercase_item_names():
    """get_item looks up by lowercased key, so each key must equal its item's name."""
    for key, item in MENU.items():
        assert key == item.name
        assert key == key.strip().lower()


@pytest.mark.parametrize("name,price", list(EXPECTED_PRICES.items()), ids=list(EXPECTED_PRICES))
def test_get_item_returns_menu_item(name, price):
    item = get_item(name)
    assert isinstance(item, Item)
    assert item.name == name
    assert item.price == price


@pytest.mark.parametrize(
    "name",
    ["Latte", "LATTE", "  latte  ", "\tlatte\n", "Blueberry Muffin", " BLUEBERRY muffin "],
    ids=["title-case", "upper-case", "padded", "tab-newline", "multiword-title", "multiword-mixed"],
)
def test_get_item_ignores_case_and_surrounding_whitespace(name):
    assert get_item(name) is MENU[name.strip().lower()]


@pytest.mark.parametrize(
    "name",
    ["mocha", "", "   ", "lat te", "blueberry  muffin", "lattes"],
    ids=["not-on-menu", "empty", "whitespace-only", "inner-space", "double-inner-space", "plural"],
)
def test_get_item_unknown_raises_key_error(name):
    with pytest.raises(KeyError):
        get_item(name)


def test_get_item_key_error_carries_original_name():
    """The 400 detail in main.py uses exc.args[0], so it must be the caller's raw input."""
    with pytest.raises(KeyError) as exc_info:
        get_item("  Mocha ")
    assert exc_info.value.args[0] == "  Mocha "


def test_menu_route_shows_price_tax_and_purchase_price():
    resp = client.get("/menu")
    assert resp.status_code == 200
    assert resp.json() == {
        "items": [
            {"name": name, "price": price, "tax": tax, "purchase_price": purchase}
            for name, price, tax, purchase in EXPECTED_MENU
        ]
    }


@pytest.mark.parametrize("name", list(EXPECTED_PRICES), ids=list(EXPECTED_PRICES))
def test_menu_purchase_price_matches_what_orders_charge(name):
    """The menu must never promise a different price than /orders charges for one item."""
    entry = next(e for e in client.get("/menu").json()["items"] if e["name"] == name)
    receipt = build_receipt(Order(items=[OrderItem(name=name, quantity=1)]))
    assert entry["tax"] == receipt.tax
    assert entry["purchase_price"] == receipt.total


def test_orders_accepts_mixed_case_item_name():
    """Lookup is case-insensitive end to end; the receipt uses the canonical name."""
    resp = client.post("/orders", json={"items": [{"name": " Latte ", "quantity": 1}]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["lines"] == [
        {"name": "latte", "quantity": 1, "unit_price": 4.82, "line_total": 4.82}
    ]
    assert body["total"] == 5.30


def test_orders_unknown_item_is_400():
    resp = client.post("/orders", json={"items": [{"name": "mocha", "quantity": 1}]})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Unknown menu item: mocha"}
