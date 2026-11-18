"""Pydantic models for brew-api."""
from __future__ import annotations

from pydantic import BaseModel


class Item(BaseModel):
    """A single menu item."""
    name: str
    price: float


class OrderItem(BaseModel):
    """One line in a cart: an item name and how many."""
    name: str
    quantity: int = 1


class Order(BaseModel):
    """A customer's cart."""
    items: list[OrderItem]
    loyalty_member: bool = False


class ReceiptLine(BaseModel):
    """A priced line on the receipt."""
    name: str
    quantity: int
    unit_price: float
    line_total: float


class Receipt(BaseModel):
    """The result of pricing an order."""
    lines: list[ReceiptLine]
    subtotal: float
    discount: float
    tax: float
    total: float


class QuoteRequest(BaseModel):
    """A cart to quote. Priced both with and without loyalty."""
    items: list[OrderItem]


class QuoteSavings(BaseModel):
    """How much a loyalty member saves on the cart."""
    discount: float
    tax: float
    total: float


class QuoteResponse(BaseModel):
    """The cart priced for a non-member and for a member, plus the savings."""
    standard: Receipt
    member: Receipt
    savings: QuoteSavings
