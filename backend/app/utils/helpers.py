"""
Shared Helper Utilities

Pure-function helpers used across the application.
This is for educational and research purposes only, not financial advice.
"""

from datetime import datetime, time, timezone, timedelta
from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Constants ─────────────────────────────────────────────────
DISCLAIMER: str = (
    "This is for educational and research purposes only, not financial advice. "
    "The creators are not responsible for any financial decisions made using "
    "this platform. Always consult a certified financial advisor."
)

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

# NSE trading hours
_MARKET_OPEN = time(9, 15)
_MARKET_CLOSE = time(15, 30)

# Monday=0 … Friday=4
_TRADING_DAYS = range(0, 5)


# ── Symbol Helpers ────────────────────────────────────────────
def validate_symbol(symbol: str) -> str:
    """
    Ensure a stock symbol carries the ``.NS`` suffix for NSE.

    Parameters
    ----------
    symbol:
        Raw symbol string, e.g. ``"RELIANCE"`` or ``"RELIANCE.NS"``.

    Returns
    -------
    str
        Symbol guaranteed to end with ``.NS``.

    Examples
    --------
    >>> validate_symbol("RELIANCE")
    'RELIANCE.NS'
    >>> validate_symbol("TCS.NS")
    'TCS.NS'
    """
    symbol = symbol.strip().upper()
    if not (symbol.endswith(".NS") or symbol.endswith(".BO")):
        symbol = f"{symbol}.NS"
    return symbol


# ── Safe Type Coercions ──────────────────────────────────────
def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert *value* to ``float``, returning *default* on failure.

    Handles ``None``, empty strings, and non-numeric objects gracefully.
    """
    if value is None:
        return default
    try:
        result = float(value)
        # Guard against NaN / Inf
        if result != result or result == float("inf") or result == float("-inf"):
            return default
        return result
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert *value* to ``int``, returning *default* on failure.
    """
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


# ── Formatting ────────────────────────────────────────────────
def format_percentage(value: float) -> str:
    """
    Format a float as a percentage string with two decimal places.

    >>> format_percentage(12.3456)
    '+12.35%'
    >>> format_percentage(-3.1)
    '-3.10%'
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_currency(value: float, currency: str = "INR") -> str:
    """
    Format a float as a currency string.

    Parameters
    ----------
    value:
        Monetary amount.
    currency:
        Currency code (default ``"INR"``).

    Returns
    -------
    str
        Formatted string, e.g. ``"₹1,23,456.78"`` for INR.
    """
    if currency == "INR":
        # Indian numbering: last 3 digits, then groups of 2
        sign = "-" if value < 0 else ""
        abs_val = abs(value)
        integer_part = int(abs_val)
        decimal_part = f"{abs_val - integer_part:.2f}"[1:]  # ".xx"

        s = str(integer_part)
        if len(s) <= 3:
            formatted = s
        else:
            # Last 3 digits
            last3 = s[-3:]
            remaining = s[:-3]
            # Group remaining in pairs from right
            groups: list[str] = []
            while remaining:
                groups.append(remaining[-2:])
                remaining = remaining[:-2]
            groups.reverse()
            formatted = ",".join(groups) + "," + last3

        return f"{sign}₹{formatted}{decimal_part}"

    # Fallback for other currencies
    return f"{currency} {value:,.2f}"


# ── Date / Time ───────────────────────────────────────────────
def get_ist_now() -> datetime:
    """Return the current date-time in Indian Standard Time (IST)."""
    return datetime.now(tz=IST)


def is_market_hours() -> bool:
    """
    Check whether the NSE market is currently open.

    The NSE trades Monday–Friday, 9:15 AM – 3:30 PM IST.
    This does **not** account for public holidays.

    Returns
    -------
    bool
        ``True`` if the current IST time falls within trading hours
        on a weekday; ``False`` otherwise.
    """
    now = get_ist_now()
    if now.weekday() not in _TRADING_DAYS:
        return False
    current_time = now.time()
    return _MARKET_OPEN <= current_time <= _MARKET_CLOSE


# ── Collection Helpers ────────────────────────────────────────
def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """
    Split *lst* into sub-lists of at most *chunk_size* elements.

    Parameters
    ----------
    lst:
        The list to split.
    chunk_size:
        Maximum number of elements per chunk (must be ≥ 1).

    Returns
    -------
    list[list]
        A list of chunks.

    Examples
    --------
    >>> chunk_list([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
