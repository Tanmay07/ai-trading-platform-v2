"""
Historical Data Service
=======================

Higher-level service for fetching historical OHLCV data, market indices,
and broad market context. Delegates raw data fetching to :class:`MarketDataService`
while adding convenience methods for multi-symbol retrieval and market overview.

Disclaimer: This is for educational and research purposes only, not financial advice.
"""

from typing import Any

import pandas as pd

from app.config import settings
from app.data.market_data_service import MarketDataService
from app.utils.helpers import validate_symbol
from app.utils.logger import get_logger


class HistoricalDataService:
    """
    Service for fetching and managing historical OHLCV data.

    Builds on top of :class:`MarketDataService` to provide higher-level
    methods such as multi-symbol batch retrieval and market-context snapshots
    (NIFTY 50, Bank NIFTY, USD/INR, Crude Oil).

    Args:
        market_data_service: An initialised MarketDataService instance.

    Usage::

        mds = MarketDataService()
        hist = HistoricalDataService(market_data_service=mds)

        df = hist.get_historical_data("TCS.NS", period="6mo")
        ctx = hist.get_market_context(period="3mo")
    """

    def __init__(self, market_data_service: MarketDataService) -> None:
        self.logger = get_logger(__name__)
        self._market_service = market_data_service

    # ------------------------------------------------------------------
    # Single symbol
    # ------------------------------------------------------------------

    def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a single symbol with validation.

        Delegates to :meth:`MarketDataService.get_ohlcv` after ensuring
        the symbol has the correct ``.NS`` suffix.

        Args:
            symbol: NSE stock symbol.
            period: Lookback period (e.g., '1y', '6mo', '3mo').
            interval: Bar interval (e.g., '1d', '1h').

        Returns:
            DataFrame with columns ``[Open, High, Low, Close, Volume]``.
            Empty DataFrame on failure.
        """
        symbol = validate_symbol(symbol)
        self.logger.info(
            "Fetching historical data for %s | period=%s, interval=%s",
            symbol,
            period,
            interval,
        )

        try:
            df = self._market_service.get_ohlcv(symbol, period=period, interval=interval)

            if df.empty:
                self.logger.warning(
                    "No historical data available for %s (period=%s)", symbol, period
                )

            return df

        except Exception as exc:
            self.logger.error(
                "Error fetching historical data for %s: %s", symbol, exc, exc_info=True
            )
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    # ------------------------------------------------------------------
    # Index data
    # ------------------------------------------------------------------

    def get_index_data(
        self,
        index: str = "^NSEI",
        period: str = "1y",
    ) -> pd.DataFrame:
        """
        Get historical data for a market index.

        Common indices:
        - ``^NSEI``    — NIFTY 50
        - ``^NSEBANK`` — Bank NIFTY

        Note: Index symbols are passed through as-is (no ``.NS`` suffix added).

        Args:
            index: Yahoo Finance index symbol.
            period: Lookback period.

        Returns:
            DataFrame with OHLCV columns. Empty DataFrame on failure.
        """
        self.logger.info("Fetching index data for %s | period=%s", index, period)

        try:
            # Index symbols don't need .NS validation — pass directly
            df = self._market_service.get_ohlcv(
                symbol=index, period=period, interval="1d"
            )

            if df.empty:
                self.logger.warning(
                    "No index data available for %s (period=%s)", index, period
                )

            return df

        except Exception as exc:
            self.logger.error(
                "Error fetching index data for %s: %s", index, exc, exc_info=True
            )
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    # ------------------------------------------------------------------
    # Multiple symbols
    # ------------------------------------------------------------------

    def get_multiple_historical(
        self,
        symbols: list[str],
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """
        Get historical data for multiple symbols.

        Iterates through the list, fetching each individually. Failures
        for a single symbol are logged but do not block the others.

        Args:
            symbols: List of NSE stock symbols.
            period: Lookback period.
            interval: Bar interval.

        Returns:
            Dictionary mapping each validated symbol to its OHLCV DataFrame.
            Symbols that failed will have an empty DataFrame.
        """
        self.logger.info(
            "Fetching historical data for %d symbols | period=%s", len(symbols), period
        )

        results: dict[str, pd.DataFrame] = {}
        for sym in symbols:
            validated = validate_symbol(sym)
            try:
                df = self.get_historical_data(validated, period=period, interval=interval)
                results[validated] = df
            except Exception as exc:
                self.logger.error(
                    "Failed to fetch historical data for %s: %s", validated, exc
                )
                results[validated] = pd.DataFrame(
                    columns=["Open", "High", "Low", "Close", "Volume"]
                )

        return results

    # ------------------------------------------------------------------
    # Market context
    # ------------------------------------------------------------------

    def get_market_context(self, period: str = "3mo") -> dict[str, Any]:
        """
        Get a broad market context snapshot.

        Fetches historical data for key market barometers:

        - **NIFTY 50** (``^NSEI``) — Indian large-cap benchmark.
        - **Bank NIFTY** (``^NSEBANK``) — Banking sector benchmark.
        - **USD/INR** (``USDINR=X``) — Currency pair.
        - **Crude Oil** (``CL=F``) — Brent crude futures proxy.

        For each instrument, a summary dictionary is returned containing
        the latest close, period return, and the raw DataFrame.

        Args:
            period: Lookback period for all instruments.

        Returns:
            Dictionary keyed by instrument label::

                {
                    "nifty50": {"close": float, "period_return": float, "data": DataFrame},
                    "banknifty": {...},
                    "usdinr": {...},
                    "crude_oil": {...},
                    "period": str,
                }
        """
        self.logger.info("Building market context | period=%s", period)

        context_symbols: dict[str, str] = {
            "nifty50": settings.MARKET_INDEX,   # ^NSEI
            "banknifty": settings.BANK_INDEX,    # ^NSEBANK
            "usdinr": "USDINR=X",
            "crude_oil": "CL=F",
        }

        context: dict[str, Any] = {"period": period}

        for label, sym in context_symbols.items():
            try:
                df = self._market_service.get_ohlcv(sym, period=period, interval="1d")

                if df.empty or "Close" not in df.columns or len(df) < 2:
                    context[label] = {
                        "close": 0.0,
                        "period_return": 0.0,
                        "data": df,
                    }
                    self.logger.warning("Insufficient data for %s (%s)", label, sym)
                    continue

                latest_close = float(df["Close"].iloc[-1])
                first_close = float(df["Close"].iloc[0])
                period_return = (
                    (latest_close - first_close) / first_close
                    if first_close != 0
                    else 0.0
                )

                context[label] = {
                    "close": round(latest_close, 2),
                    "period_return": round(period_return, 4),
                    "data": df,
                }
                self.logger.debug(
                    "%s: close=%.2f, period_return=%.4f",
                    label,
                    latest_close,
                    period_return,
                )

            except Exception as exc:
                self.logger.error(
                    "Error fetching market context for %s (%s): %s",
                    label,
                    sym,
                    exc,
                    exc_info=True,
                )
                context[label] = {
                    "close": 0.0,
                    "period_return": 0.0,
                    "data": pd.DataFrame(),
                    "error": str(exc),
                }

        return context
