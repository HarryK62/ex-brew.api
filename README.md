# brew-api

The ordering backend for **Maple & Main Coffee**. A small [FastAPI](https://fastapi.tiangolo.com/)
service that serves the menu and prices orders. This is the sample repo for the
**7-Day Claude for Developers Challenge** — small, real, and with a few surprises
waiting, just like code you inherit at work.

## Endpoints

| Method | Path      | Purpose                          |
|--------|-----------|----------------------------------|
| GET    | `/health` | Liveness check                   |
| GET    | `/menu`   | The full menu                    |
| POST   | `/orders` | Price a cart and return a receipt |

## Project layout

```
app/
  main.py       FastAPI app and routes
  models.py     Pydantic models (Order, Receipt, ...)
  menu.py       the menu and get_item()
  orders.py     pricing — build_receipt()
  summary.py    order_total() helper
  customers.py  customer lookup (added by an open PR — see Day 5)
tests/          the test suite
```

## Pricing

All menu prices are **tax-inclusive** — the price on the menu is the price the
customer pays. Loyalty members get 10% off.

## Getting started

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the tests:

```bash
pytest -q
```
