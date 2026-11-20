"""Pydantic models for brew-api."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Item(BaseModel):
    """A single menu item."""
    name: str
    price: float


class MenuEntry(BaseModel):
    """A menu line as customers see it: pre-tax price, the tax added, and what they pay."""
    name: str
    price: float
    tax: float
    purchase_price: float


class OrderItem(BaseModel):
    """One line in a cart: an item name and how many."""
    name: str
    quantity: int = Field(default=1, ge=1)  # reject zero or negative quantities


class Order(BaseModel):
    """A customer's cart."""
    items: list[OrderItem]
    loyalty_member: bool = False
    promo_code: str | None = None  # e.g. "MAPLE10"; case and spaces don't matter


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
    discount: float  # loyalty discount
    promo_discount: float = 0.0
    tax: float
    total: float


class QuoteRequest(BaseModel):
    """A cart to quote. Priced both with and without loyalty."""
    items: list[OrderItem]
    promo_code: str | None = None


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
