"""
Live Data Service
=================

Provides a TTL-based caching layer on top of :class:`MarketDataService` so that
frequently-requested symbols (e.g., watchlist tickers shown on a dashboard)
don't hammer the Yahoo Finance API on every call.

Cache entries expire after ``settings.CACHE_TTL_SECONDS`` (default 300 s / 5 min).

Disclaimer: This is for educational and research purposes only, not financial advice.
"""

import time
from typing import Any

from app.config import settings
from app.data.market_data_service import MarketDataService
from app.utils.helpers import validate_symbol
from app.utils.logger import get_logger


class LiveDataService:
    """
    Provides cached live market data with TTL-based refresh.

    Wraps a :class:`MarketDataService` instance and keeps a per-symbol
    in-memory cache.  When a caller requests data, the service checks
    the cache first and only fetches fresh data from Yahoo Finance
    if the cached entry has expired.

    Args:
        market_data_service: An initialised MarketDataService instance.

    Usage::

        mds = MarketDataService()
        live = LiveDataService(market_data_service=mds)
        snapshot = live.get_live_snapshot("INFY.NS")
        watchlist = live.get_watchlist_data()  # uses DEFAULT_WATCHLIST
    """

    def __init__(self, market_data_service: MarketDataService) -> None:
        self.logger = get_logger(__name__)
        self._market_service = market_data_service
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_ttl: int = settings.CACHE_TTL_SECONDS
        self.logger.info(
            "LiveDataService initialised with cache TTL = %d s", self._cache_ttl
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_live_snapshot(self, symbol: str) -> dict[str, Any]:
        """
        Get cached live data for a single symbol, refreshing if stale.

        Args:
            symbol: NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS').

        Returns:
            Price data dictionary from :meth:`MarketDataService.get_current_price`,
            enriched with a ``cached`` boolean flag.
        """
        symbol = validate_symbol(symbol)

        if self._is_cache_valid(symbol):
            self.logger.debug("Cache HIT for %s", symbol)
            data = self._cache[symbol]["data"].copy()
            data["cached"] = True
            return data

        self.logger.debug("Cache MISS for %s — fetching fresh data", symbol)
        data = self._market_service.get_current_price(symbol)

        # Store in cache regardless of error — avoids hammering on repeated failures
        self._cache[symbol] = {
            "data": data,
            "timestamp": time.time(),
        }

        data_copy = data.copy()
        data_copy["cached"] = False
        return data_copy

    def get_watchlist_data(
        self, symbols: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get live data for a list of watchlist symbols.

        If ``symbols`` is not provided, falls back to
        ``settings.DEFAULT_WATCHLIST``.

        Args:
            symbols: Optional list of NSE stock symbols.

        Returns:
            List of price-data dictionaries, one per symbol.
        """
        if symbols is None:
            symbols = list(settings.DEFAULT_WATCHLIST)

        self.logger.info("Fetching watchlist data for %d symbols", len(symbols))

        results: list[dict[str, Any]] = []
        for sym in symbols:
            try:
                snapshot = self.get_live_snapshot(sym)
                results.append(snapshot)
            except Exception as exc:
                self.logger.error(
                    "Error fetching live snapshot for %s: %s", sym, exc
                )
                results.append(
                    {
                        "symbol": validate_symbol(sym),
                        "price": 0.0,
                        "error": str(exc),
                        "cached": False,
                    }
                )

        return results

    def invalidate_cache(self, symbol: str | None = None) -> None:
        """
        Clear cache for a specific symbol or the entire cache.

        Args:
            symbol: If provided, remove only this symbol's cache entry.
                    If ``None``, clear the entire cache.
        """
        if symbol:
            symbol = validate_symbol(symbol)
            removed = self._cache.pop(symbol, None)
            if removed:
                self.logger.debug("Invalidated cache for %s", symbol)
            else:
                self.logger.debug("No cache entry to invalidate for %s", symbol)
        else:
            count = len(self._cache)
            self._cache.clear()
            self.logger.debug("Cleared entire cache (%d entries)", count)

    # ------------------------------------------------------------------
    # Cache internals
    # ------------------------------------------------------------------

    def _is_cache_valid(self, symbol: str) -> bool:
        """
        Check whether the cached data for ``symbol`` is within the TTL window.

        Args:
            symbol: Validated NSE symbol.

        Returns:
            ``True`` if a cache entry exists and has not expired.
        """
        entry = self._cache.get(symbol)
        if entry is None:
            return False

        age = time.time() - entry["timestamp"]
        return age < self._cache_ttl

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def cache_size(self) -> int:
        """Number of symbols currently in the cache."""
        return len(self._cache)

    def get_cache_status(self) -> dict[str, Any]:
        """
        Return diagnostic info about the current cache state.

        Returns:
            Dictionary with ``size``, ``ttl_seconds``, and per-symbol ``entries``
            showing age in seconds.
        """
        now = time.time()
        entries: dict[str, float] = {}
        for sym, entry in self._cache.items():
            entries[sym] = round(now - entry["timestamp"], 1)

        return {
            "size": len(self._cache),
            "ttl_seconds": self._cache_ttl,
            "entries_age_seconds": entries,
        }
