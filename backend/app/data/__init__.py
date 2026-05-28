"""
Data Services Package
=====================

This package contains the three data service layers:

- :class:`MarketDataService` — Core yfinance wrapper for fetching prices,
  OHLCV history, and stock metadata.
- :class:`LiveDataService` — TTL-based caching layer for dashboard /
  watchlist use cases.
- :class:`HistoricalDataService` — Higher-level historical data access
  with multi-symbol and market-context support.

Usage::

    from app.data import MarketDataService, LiveDataService, HistoricalDataService

    mds = MarketDataService()
    live = LiveDataService(market_data_service=mds)
    hist = HistoricalDataService(market_data_service=mds)
"""

from app.data.historical_data_service import HistoricalDataService
from app.data.live_data_service import LiveDataService
from app.data.market_data_service import MarketDataService

__all__ = [
    "MarketDataService",
    "LiveDataService",
    "HistoricalDataService",
]
