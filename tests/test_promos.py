from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Order, OrderItem
from app.orders import build_receipt
import app.promos as promos
from app.promos import PROMO_CODES, PromoNotActive, normalize_code, promo_rate

client = TestClient(app)

MAPLE10_FIRST_DAY = date(2026, 11, 20)
MAPLE10_LAST_DAY = date(2026, 12, 19)


@pytest.fixture(autouse=True)
def promo_is_live(monkeypatch):
    """Pin "today" inside the MAPLE10 window so these tests don't start failing
    once the real promo ends. Window tests override it with set_today."""
    monkeypatch.setattr(promos, "today", lambda: date(2026, 12, 1))


@pytest.fixture
def set_today(monkeypatch):
    def _set(day):
        monkeypatch.setattr(promos, "today", lambda: day)
    return _set

CART = [
    {"name": "latte", "quantity": 2},
    {"name": "blueberry muffin", "quantity": 1},
]  # subtotal 13.39


def _order(**kwargs):
    return Order(items=[OrderItem(**i) for i in CART], **kwargs)


def test_promo_non_member():
    receipt = build_receipt(_order(promo_code="MAPLE10"))
    assert receipt.subtotal == 13.39
    assert receipt.discount == 0.0
    assert receipt.promo_discount == 1.34
    assert receipt.tax == 1.21
    assert receipt.total == 13.26


def test_promo_stacks_with_loyalty_off_the_subtotal():
    """Both discounts are 10% of the subtotal, so a member with the code saves 20%."""
    receipt = build_receipt(_order(loyalty_member=True, promo_code="MAPLE10"))
    assert receipt.discount == 1.34
    assert receipt.promo_discount == 1.34
    assert receipt.tax == 1.07  # 10% of 10.71
    assert receipt.total == 11.78


@pytest.mark.parametrize("code", [None, "", "   "], ids=["missing", "empty", "blank"])
def test_no_code_prices_as_before(code):
    with_code = build_receipt(_order(loyalty_member=True, promo_code=code))
    assert with_code == build_receipt(_order(loyalty_member=True))
    assert with_code.promo_discount == 0.0


@pytest.mark.parametrize(
    "code", ["MAPLE10", "maple10", " Maple10 ", "\tMAPLE10\n"],
    ids=["exact", "lower", "padded-mixed", "tab-newline"],
)
def test_code_ignores_case_and_whitespace(code):
    assert normalize_code(code) == "MAPLE10"
    assert promo_rate(code) == 0.10


@pytest.mark.parametrize("code", ["MAPLE20", "MAPLE 10", "maple10x"], ids=["other", "inner-space", "suffix"])
def test_unknown_code_raises_key_error(code):
    with pytest.raises(KeyError) as exc_info:
        promo_rate(code)
    assert exc_info.value.args[0] == code


def test_empty_cart_with_code_is_zero():
    receipt = build_receipt(Order(items=[], loyalty_member=True, promo_code="MAPLE10"))
    assert (receipt.subtotal, receipt.discount, receipt.promo_discount, receipt.tax, receipt.total) == (0, 0, 0, 0, 0)


def test_orders_route_applies_promo():
    resp = client.post("/orders", json={"items": CART, "loyalty_member": True, "promo_code": "maple10"})
    assert resp.status_code == 200
    assert resp.json()["promo_discount"] == 1.34
    assert resp.json()["total"] == 11.78


@pytest.mark.parametrize("path", ["/orders", "/quote"])
def test_unknown_code_is_400(path):
    resp = client.post(path, json={"items": CART, "promo_code": "FREECOFFEE"})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Unknown promo code: FREECOFFEE"}


def test_quote_with_code_matches_build_receipt():
    """The quote must never drift from what /orders charges, with a code too."""
    body = client.post("/quote", json={"items": CART, "promo_code": "MAPLE10"}).json()
    assert body["standard"] == build_receipt(_order(promo_code="MAPLE10")).model_dump()
    assert body["member"] == build_receipt(_order(loyalty_member=True, promo_code="MAPLE10")).model_dump()
    assert body["standard"]["total"] == 13.26
    assert body["member"]["total"] == 11.78
    # Savings show what loyalty adds on top of the promo.
    assert body["savings"] == {"discount": 1.34, "tax": 0.14, "total": 1.48}


def test_maple10_runs_for_30_days():
    promo = PROMO_CODES["MAPLE10"]
    assert (promo.starts, promo.ends) == (MAPLE10_FIRST_DAY, MAPLE10_LAST_DAY)
    assert (promo.ends - promo.starts).days + 1 == 30


@pytest.mark.parametrize(
    "day", [MAPLE10_FIRST_DAY, date(2026, 12, 5), MAPLE10_LAST_DAY],
    ids=["first-day", "mid", "last-day"],
)
def test_code_works_inside_window(day):
    assert promo_rate("MAPLE10", on=day) == 0.10


@pytest.mark.parametrize(
    "day, message",
    [
        (date(2026, 12, 20), "Promo code MAPLE10 expired on 2026-12-19"),
        (date(2027, 6, 1), "Promo code MAPLE10 expired on 2026-12-19"),
        (date(2026, 11, 19), "Promo code MAPLE10 starts on 2026-11-20"),
    ],
    ids=["day-after-end", "months-later", "day-before-start"],
)
def test_code_rejected_outside_window(day, message):
    with pytest.raises(PromoNotActive, match=message):
        promo_rate("maple10", on=day)


@pytest.mark.parametrize("path", ["/orders", "/quote"])
def test_expired_code_is_400(path, set_today):
    set_today(date(2026, 12, 20))
    resp = client.post(path, json={"items": CART, "promo_code": "MAPLE10"})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Promo code MAPLE10 expired on 2026-12-19"}


def test_order_without_code_still_works_after_promo_ends(set_today):
    set_today(date(2026, 12, 20))
    resp = client.post("/orders", json={"items": CART, "loyalty_member": True})
    assert resp.status_code == 200
    assert resp.json()["promo_discount"] == 0.0
    assert resp.json()["total"] == 13.26
