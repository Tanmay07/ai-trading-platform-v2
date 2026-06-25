"""
Market Data Service
===================

Core service for fetching real-time and historical market data from Yahoo Finance
via the ``yfinance`` library. All other data services build on top of this one.

Handles NSE-listed equities (symbols ending with .NS) and common indices
(^NSEI for NIFTY 50, ^NSEBANK for Bank Nifty).

Disclaimer: This is for educational and research purposes only, not financial advice.
"""

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf

from app.config import settings
from app.utils.helpers import DISCLAIMER, safe_float, validate_symbol
from app.utils.logger import get_logger

# Valid periods and intervals accepted by yfinance
_VALID_PERIODS = {
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max",
}
_VALID_INTERVALS = {
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "1d", "5d", "1wk", "1mo", "3mo",
}


class MarketDataService:
    """
    Service for fetching market data from Yahoo Finance for NSE stocks.

    Provides methods for current price lookup, OHLCV history, batch quotes,
    and stock metadata. All yfinance calls are wrapped in try/except blocks
    to ensure graceful degradation.

    Usage::

        service = MarketDataService()
        price_data = service.get_current_price("RELIANCE.NS")
        ohlcv_df = service.get_ohlcv("TCS.NS", period="6mo")
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        # In-memory cache for stock info (rarely changes)
        self._info_cache: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Current / latest price
    # ------------------------------------------------------------------

    def get_current_price(self, symbol: str) -> dict[str, Any]:
        """
        Get current / latest price data for a single symbol.

        Uses ``yfinance.Ticker.fast_info`` for speed, falling back to
        ``Ticker.info`` if fast_info is insufficient.

        Args:
            symbol: NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS').

        Returns:
            Dictionary with keys::

                {
                    "symbol": str,
                    "price": float,
                    "change": float,
                    "change_pct": float,
                    "volume": int,
                    "high": float,
                    "low": float,
                    "open": float,
                    "prev_close": float,
                    "timestamp": str (ISO 8601),
                    "disclaimer": str,
                }

            On failure, ``price`` will be 0.0 and an ``error`` key is added.
        """
        symbol = validate_symbol(symbol)
        self.logger.debug("Fetching current price for %s", symbol)

        result: dict[str, Any] = {
            "symbol": symbol,
            "price": 0.0,
            "change": 0.0,
            "change_pct": 0.0,
            "volume": 0,
            "high": 0.0,
            "low": 0.0,
            "open": 0.0,
            "prev_close": 0.0,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "disclaimer": DISCLAIMER,
        }

        try:
            ticker = yf.Ticker(symbol)

            # fast_info is the lightweight path
            fi = ticker.fast_info
            price = safe_float(getattr(fi, "last_price", None))
            prev_close = safe_float(getattr(fi, "previous_close", None))
            day_high = safe_float(getattr(fi, "day_high", None))
            day_low = safe_float(getattr(fi, "day_low", None))
            open_price = safe_float(getattr(fi, "open", None))
            volume = int(safe_float(getattr(fi, "last_volume", None)))

            # If fast_info didn't return a price, try .info dict
            if price == 0.0:
                info = ticker.info or {}
                price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
                prev_close = safe_float(info.get("previousClose") or info.get("regularMarketPreviousClose", prev_close))
                day_high = safe_float(info.get("dayHigh") or info.get("regularMarketDayHigh", day_high))
                day_low = safe_float(info.get("dayLow") or info.get("regularMarketDayLow", day_low))
                open_price = safe_float(info.get("open") or info.get("regularMarketOpen", open_price))
                volume = int(safe_float(info.get("volume") or info.get("regularMarketVolume", volume)))

            change = price - prev_close if prev_close else 0.0
            change_pct = (change / prev_close * 100) if prev_close else 0.0

            result.update(
                {
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": volume,
                    "high": day_high,
                    "low": day_low,
                    "open": open_price,
                    "prev_close": prev_close,
                }
            )
        except Exception as e:
            self.logger.error("Failed to fetch current price for %s via yfinance: %s", symbol, e)
            
            # Google Finance Fallback when yfinance is rate limited
            try:
                import requests
                import re
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                exchange = 'NSE' if '.NS' in symbol else ('BOM' if '.BO' in symbol else 'NSE')
                url = f"https://www.google.com/finance/quote/{clean_symbol}:{exchange}"
                res = requests.get(url, timeout=5)
                match = re.search(r'class="YMlKec fxKbKc">₹?([0-9,.]+)<', res.text)
                if match:
                    fallback_price = float(match.group(1).replace(",", ""))
                    result["price"] = fallback_price
                    self.logger.info("Successfully fetched %s from Google Finance fallback", symbol)
                    return result
            except Exception as gf_e:
                self.logger.error("Google finance fallback failed for %s: %s", symbol, gf_e)
                
            result["error"] = str(e)

        return result

    # ------------------------------------------------------------------
    # OHLCV historical data
    # ------------------------------------------------------------------

    def get_ohlcv(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Get OHLCV historical data for a symbol.

        Args:
            symbol: NSE stock symbol (auto-validated to include .NS suffix).
            period: Lookback period — one of '1d','5d','1mo','3mo','6mo',
                    '1y','2y','5y','10y','ytd','max'.
            interval: Bar interval — e.g., '1d','1h','5m'.

        Returns:
            A ``pd.DataFrame`` with columns ``[Open, High, Low, Close, Volume]``.
            Returns an empty DataFrame on failure.
        """
        symbol = validate_symbol(symbol)

        if period not in _VALID_PERIODS:
            self.logger.warning(
                "Invalid period '%s' for %s, defaulting to '1y'", period, symbol
            )
            period = "1y"
        if interval not in _VALID_INTERVALS:
            self.logger.warning(
                "Invalid interval '%s' for %s, defaulting to '1d'", interval, symbol
            )
            interval = "1d"

        self.logger.debug(
            "Fetching OHLCV for %s | period=%s, interval=%s", symbol, period, interval
        )

        try:
            ticker = yf.Ticker(symbol)
            df: pd.DataFrame = ticker.history(period=period, interval=interval)

            if df.empty:
                self.logger.warning("No OHLCV data returned for %s", symbol)
                return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

            # Keep only the essential OHLCV columns
            expected_cols = ["Open", "High", "Low", "Close", "Volume"]
            available_cols = [c for c in expected_cols if c in df.columns]
            df = df[available_cols].copy()

            # Drop rows where Close is NaN (data quality guard)
            df.dropna(subset=["Close"], inplace=True)

            self.logger.info(
                "Fetched %d bars for %s (%s / %s)", len(df), symbol, period, interval
            )
            return df

        except Exception as exc:
            self.logger.error(
                "Failed to fetch OHLCV for %s: %s", symbol, exc, exc_info=True
            )
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    # ------------------------------------------------------------------
    # Multiple quotes (batch)
    # ------------------------------------------------------------------

    def get_multiple_quotes(self, symbols: list[str]) -> list[dict[str, Any]]:
        """
        Get current price data for multiple symbols.

        Iterates through the symbol list and calls :meth:`get_current_price`
        for each. Individual failures are logged but do not prevent other
        symbols from being fetched.

        Args:
            symbols: List of NSE stock symbols.

        Returns:
            List of price data dictionaries (one per symbol). Failed symbols
            still appear in the list with ``price=0.0`` and an ``error`` key.
        """
        self.logger.debug("Fetching quotes for %d symbols", len(symbols))
        results: list[dict[str, Any]] = []

        for sym in symbols:
            try:
                quote = self.get_current_price(sym)
                results.append(quote)
            except Exception as exc:
                self.logger.error(
                    "Unexpected error fetching quote for %s: %s", sym, exc
                )
                results.append(
                    {
                        "symbol": validate_symbol(sym),
                        "price": 0.0,
                        "error": str(exc),
                        "disclaimer": DISCLAIMER,
                    }
                )

        return results

    # ------------------------------------------------------------------
    # Stock metadata / info
    # ------------------------------------------------------------------

    def get_stock_info(self, symbol: str) -> dict[str, Any]:
        """
        Get stock metadata: name, sector, industry, market cap, etc.

        Results are cached in memory because metadata changes infrequently.

        Args:
            symbol: NSE stock symbol.

        Returns:
            Dictionary with keys::

                {
                    "symbol": str,
                    "name": str,
                    "sector": str,
                    "industry": str,
                    "market_cap": float,
                    "pe_ratio": float,
                    "pb_ratio": float,
                    "dividend_yield": float,
                    "52w_high": float,
                    "52w_low": float,
                    "description": str,
                    "disclaimer": str,
                }
        """
        symbol = validate_symbol(symbol)

        # Return cached result if available
        if symbol in self._info_cache:
            self.logger.debug("Returning cached info for %s", symbol)
            return self._info_cache[symbol]

        self.logger.debug("Fetching stock info for %s", symbol)

        info_result: dict[str, Any] = {
            "symbol": symbol,
            "name": "",
            "sector": "",
            "industry": "",
            "market_cap": 0.0,
            "pe_ratio": 0.0,
            "pb_ratio": 0.0,
            "dividend_yield": 0.0,
            "52w_high": 0.0,
            "52w_low": 0.0,
            "description": "",
            "disclaimer": DISCLAIMER,
        }

        try:
            ticker = yf.Ticker(symbol)
            info: dict[str, Any] = ticker.info or {}

            info_result.update(
                {
                    "name": info.get("longName") or info.get("shortName", ""),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "market_cap": safe_float(info.get("marketCap")),
                    "pe_ratio": safe_float(info.get("trailingPE")),
                    "pb_ratio": safe_float(info.get("priceToBook")),
                    "dividend_yield": safe_float(info.get("dividendYield")),
                    "52w_high": safe_float(info.get("fiftyTwoWeekHigh")),
                    "52w_low": safe_float(info.get("fiftyTwoWeekLow")),
                    "description": info.get("longBusinessSummary", ""),
                }
            )

            # Cache the result
            self._info_cache[symbol] = info_result
            self.logger.info("Fetched and cached info for %s", symbol)

        except Exception as exc:
            self.logger.error(
                "Failed to fetch stock info for %s: %s", symbol, exc, exc_info=True
            )
            info_result["error"] = str(exc)

        return info_result

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def clear_info_cache(self, symbol: str | None = None) -> None:
        """
        Clear the in-memory stock info cache.

        Args:
            symbol: If provided, clear only this symbol's cache entry.
                    If None, clear the entire cache.
        """
        if symbol:
            symbol = validate_symbol(symbol)
            self._info_cache.pop(symbol, None)
            self.logger.debug("Cleared info cache for %s", symbol)
        else:
            self._info_cache.clear()
            self.logger.debug("Cleared entire info cache")
