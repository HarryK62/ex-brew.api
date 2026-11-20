# brew-api

The ordering backend for **Maple & Main Coffee**. A small [FastAPI](https://fastapi.tiangolo.com/)
service that serves the menu and prices orders. This is the sample repo for the
**7-Day Claude for Developers Challenge** — small, real, and with a few surprises
waiting, just like code you inherit at work.

## Endpoints

| Method | Path      | Purpose                          |
|--------|-----------|----------------------------------|
| GET    | `/health` | Liveness check                   |
| GET    | `/menu`   | The menu, with tax and purchase price |
| POST   | `/orders` | Price a cart and return a receipt |

## Project layout

```
app/
  main.py       FastAPI app and routes
  models.py     Pydantic models (Order, Receipt, ...)
  menu.py       the menu and get_item()
  orders.py     pricing — build_receipt()
  promos.py     promo codes (MAPLE10)
  summary.py    order_total() helper
  customers.py  customer lookup (added by an open PR — see Day 5)
tests/          the test suite
```

## Pricing

Menu prices are **before tax**. A 10% tax is added on top, after any loyalty
discount. `GET /menu` shows each item's price, the tax added and the purchase
price, so a latte reads 4.82 + 0.48 tax = 5.30. Loyalty members get 10% off.

**Promo codes.** Send `"promo_code": "MAPLE10"` with an order or quote to take
another 10% off. It stacks with loyalty, and both discounts come off the
subtotal, so a member using the code saves 20% before tax. MAPLE10 runs for 30 days,
2026-11-20 to 2026-12-19 inclusive. Capitals and spaces in the code are ignored.
An unknown, expired or not-yet-started code returns a 400. Codes live in
`app/promos.py`.

## Getting started

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set BREW_API_KEY in .env
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the tests:

```bash
pytest -q
```
