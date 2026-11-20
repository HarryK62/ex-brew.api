"""Promo codes, their discount rates and the dates they run.

Each code takes its rate off the order subtotal. It stacks with the loyalty
discount, and both come off the subtotal, so a loyalty member using MAPLE10
saves 20% before tax.
"""
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Promo:
    """A promo code's rate and the first and last days it can be used."""
    rate: float
    starts: date
    ends: date  # last valid day, inclusive

    def is_active(self, on: date) -> bool:
        return self.starts <= on <= self.ends


class PromoNotActive(ValueError):
    """The code exists but can't be used today (expired or not started)."""


MAPLE10_START = date(2026, 11, 20)

# Valid codes, upper-case.
PROMO_CODES = {
    # Launch promo: 30 days, 2026-11-20 to 2026-12-19 inclusive.
    "MAPLE10": Promo(rate=0.10, starts=MAPLE10_START,
                     ends=MAPLE10_START + timedelta(days=29)),
}


def today() -> date:
    """The current date on the server. Tests monkeypatch this."""
    return date.today()


def normalize_code(code: str | None) -> str | None:
    """Upper-case and trim a code. A missing or blank code becomes None."""
    if code is None:
        return None
    code = code.strip().upper()
    return code or None


def promo_rate(code: str | None, on: date | None = None) -> float:
    """Return the discount rate for ``code`` on date ``on`` (default today).

    Returns 0.0 when there is no code. Raises KeyError with the code as typed
    if it isn't a valid code, and PromoNotActive if it is outside its dates.
    Routes turn both into a 400.
    """
    key = normalize_code(code)
    if key is None:
        return 0.0
    if key not in PROMO_CODES:
        raise KeyError(code)
    promo = PROMO_CODES[key]
    on = on or today()
    if on > promo.ends:
        raise PromoNotActive(f"Promo code {key} expired on {promo.ends.isoformat()}")
    if on < promo.starts:
        raise PromoNotActive(f"Promo code {key} starts on {promo.starts.isoformat()}")
    return promo.rate
