"""Promo codes and their discount rates.

Each code takes its rate off the order subtotal. It stacks with the loyalty
discount, and both come off the subtotal, so a loyalty member using MAPLE10
saves 20% before tax.
"""

# Valid codes, upper-case, mapped to the share of the subtotal they take off.
PROMO_CODES = {
    "MAPLE10": 0.10,  # launch promo, 2026-11
}


def normalize_code(code: str | None) -> str | None:
    """Upper-case and trim a code. A missing or blank code becomes None."""
    if code is None:
        return None
    code = code.strip().upper()
    return code or None


def promo_rate(code: str | None) -> float:
    """Return the discount rate for ``code``, or 0.0 when there is no code.

    Raises KeyError with the code as typed if it is not a valid code;
    routes turn that into a 400.
    """
    key = normalize_code(code)
    if key is None:
        return 0.0
    if key not in PROMO_CODES:
        raise KeyError(code)
    return PROMO_CODES[key]
