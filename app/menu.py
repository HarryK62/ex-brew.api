"""The Maple & Main menu, and a helper to look items up."""
from app.models import Item

# The menu, keyed by lowercase item name. Prices are before tax.
# 2026-11-20: prices raised 7% (rounded to the cent); previous menu in menu.py.old.
MENU = {
    "latte": Item(name="latte", price=4.82),
    "cappuccino": Item(name="cappuccino", price=4.55),
    "espresso": Item(name="espresso", price=3.21),
    "americano": Item(name="americano", price=4.01),
    "blueberry muffin": Item(name="blueberry muffin", price=3.75),
    "croissant": Item(name="croissant", price=3.48),
}


def get_item(name: str) -> Item:
    """Return the menu Item for ``name``.

    Raises KeyError if the item is not on the menu; callers turn that into
    a 400 so a bad cart doesn't 500.
    """
    key = name.strip().lower()
    if key not in MENU:
        raise KeyError(name)
    return MENU[key]
