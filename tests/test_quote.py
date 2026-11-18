from fastapi.testclient import TestClient

from app.main import app
from app.models import Order, OrderItem
from app.orders import build_receipt

client = TestClient(app)

CART = [
    {"name": "latte", "quantity": 2},
    {"name": "blueberry muffin", "quantity": 1},
]


def test_quote_shows_loyalty_savings():
    resp = client.post("/quote", json={"items": CART})
    assert resp.status_code == 200
    body = resp.json()
    assert body["standard"]["total"] == 13.50
    assert body["member"]["total"] == 12.15
    # Members save the 10% discount plus the tax on that discount.
    assert body["savings"] == {"discount": 1.25, "tax": 0.10, "total": 1.35}


def test_quote_rounding_cart():
    """1 latte + 1 cappuccino: the discount rounds 0.875 up to 0.88."""
    cart = [{"name": "latte", "quantity": 1}, {"name": "cappuccino", "quantity": 1}]
    body = client.post("/quote", json={"items": cart}).json()
    assert body["member"]["discount"] == 0.88
    assert body["member"]["total"] == 8.50
    assert body["standard"]["total"] == 9.45
    assert body["savings"]["total"] == 0.95


def test_quote_matches_build_receipt():
    """The quote must never drift from what /orders charges."""
    items = [OrderItem(**i) for i in CART]
    body = client.post("/quote", json={"items": CART}).json()
    assert body["standard"] == build_receipt(Order(items=items)).model_dump()
    assert body["member"] == build_receipt(Order(items=items, loyalty_member=True)).model_dump()


def test_quote_unknown_item_is_400():
    resp = client.post("/quote", json={"items": [{"name": "mocha", "quantity": 1}]})
    assert resp.status_code == 400
    assert "mocha" in resp.json()["detail"]


def test_quote_empty_cart_is_zero():
    resp = client.post("/quote", json={"items": []})
    assert resp.status_code == 200
    assert resp.json()["savings"] == {"discount": 0.0, "tax": 0.0, "total": 0.0}
