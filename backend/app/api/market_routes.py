"""
Market Data API routes.

Provides endpoints for live market data, historical OHLCV with indicators,
and watchlist snapshots.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.data.historical_data_service import HistoricalDataService
from app.data.market_data_service import MarketDataService
from app.data.screener_service import ScreenerService
from app.features.feature_pipeline import FeaturePipeline
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Market Data"])

# Shared service instances (stateless, safe to reuse)
_market_svc = MarketDataService()
_history_svc = HistoricalDataService(market_data_service=_market_svc)
_feature_pipeline = FeaturePipeline()
_screener_svc = ScreenerService()


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.get("/live/{symbol}")
async def get_live_data(symbol: str) -> dict[str, Any]:
    """Get live market data for a symbol.

    Returns the current price, day change, volume, and a snapshot of
    key technical indicators computed on the most recent daily data.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE`` or ``RELIANCE.NS``).

    Returns:
        JSON with current price, change, volume, and key indicators.
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /market/live/%s", symbol)

    try:
        loop = asyncio.get_running_loop()

        # Fetch live price (blocking yfinance call → run in executor)
        price_data: dict = await loop.run_in_executor(
            None, partial(_market_svc.get_current_price, symbol)
        )

        # Fetch a short history to compute a few indicators
        df = await loop.run_in_executor(
            None,
            partial(_history_svc.get_historical_data, symbol, period="3mo", interval="1d"),
        )

        indicators: dict[str, Any] = {}
        if df is not None and not df.empty:
            df_feat = _feature_pipeline.compute_all_features(df)
            last = df_feat.iloc[-1]
            indicators = {
                "rsi": _safe(last, "rsi"),
                "sma_20": _safe(last, "sma_20"),
                "sma_50": _safe(last, "sma_50"),
                "macd_histogram": _safe(last, "macd_histogram"),
                "atr": _safe(last, "atr"),
                "volume_ratio": _safe(last, "volume_ratio"),
            }

        return {
            "symbol": symbol,
            **price_data,
            "indicators": indicators,
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error fetching live data for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch live data: {exc}")


@router.get("/history/{symbol}")
async def get_history(
    symbol: str,
    period: str = Query(default="1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query(default="1d", description="Interval: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo"),
) -> dict[str, Any]:
    """Get historical OHLCV data with technical indicators.

    The response includes raw OHLCV rows *and* a summary of the latest
    indicator values.

    Args:
        symbol: NSE stock symbol.
        period: Look-back period (yfinance format).
        interval: Data granularity.

    Returns:
        JSON with ``symbol``, ``period``, ``interval``, ``data`` (list of
        OHLCV dicts), and ``indicators`` (latest values).
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /market/history/%s  period=%s  interval=%s", symbol, period, interval)

    try:
        loop = asyncio.get_running_loop()

        df = await loop.run_in_executor(
            None,
            partial(_history_svc.get_historical_data, symbol, period=period, interval=interval),
        )

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")

        # Compute features
        df_feat = _feature_pipeline.compute_all_features(df)

        # Prepare OHLCV rows (limit to avoid huge payloads)
        records = df_feat.reset_index().tail(500).to_dict(orient="records")
        # Convert Timestamps to strings for JSON serialisation
        for rec in records:
            for key, val in rec.items():
                if hasattr(val, "isoformat"):
                    rec[key] = val.isoformat()

        # Latest indicator summary
        last = df_feat.iloc[-1]
        indicators = {
            "rsi": _safe(last, "rsi"),
            "sma_20": _safe(last, "sma_20"),
            "sma_50": _safe(last, "sma_50"),
            "sma_200": _safe(last, "sma_200"),
            "ema_12": _safe(last, "ema_12"),
            "ema_26": _safe(last, "ema_26"),
            "macd": _safe(last, "macd"),
            "macd_signal": _safe(last, "macd_signal"),
            "macd_histogram": _safe(last, "macd_histogram"),
            "bb_upper": _safe(last, "bb_upper"),
            "bb_middle": _safe(last, "bb_middle"),
            "bb_lower": _safe(last, "bb_lower"),
            "atr": _safe(last, "atr"),
            "stoch_k": _safe(last, "stoch_k"),
            "stoch_d": _safe(last, "stoch_d"),
            "volume_ratio": _safe(last, "volume_ratio"),
        }

        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(records),
            "data": records,
            "indicators": indicators,
            "disclaimer": DISCLAIMER,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error fetching history for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {exc}")


@router.get("/watchlist")
async def get_watchlist() -> dict[str, Any]:
    """Get live data for the default watchlist stocks.

    Fetches current price and basic info for each symbol in
    ``settings.DEFAULT_WATCHLIST``.

    Returns:
        JSON with ``watchlist`` list and ``count``.
    """
    symbols = list(settings.DEFAULT_WATCHLIST)
    logger.info("GET /market/watchlist — %d symbols", len(symbols))

    try:
        loop = asyncio.get_running_loop()
        quotes_list = await loop.run_in_executor(
            None, partial(_market_svc.get_multiple_quotes, symbols)
        )
        quotes = {q["symbol"]: q for q in quotes_list}

        watchlist: list[dict] = []
        for sym in symbols:
            data = quotes.get(sym, {})
            watchlist.append({"symbol": sym, **data})

        return {
            "watchlist": watchlist,
            "count": len(watchlist),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error fetching watchlist: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch watchlist: {exc}")


@router.get("/sectors")
async def get_sectors() -> dict[str, Any]:
    """Get market stocks grouped by sector with live quotes.

    Returns:
        JSON with sector names mapping to a list of dicts with symbol and price data.
    """
    logger.info("GET /market/sectors")
    try:
        sectors = await _screener_svc.get_sectors()
        
        # Flatten all symbols to fetch quotes in one batch
        all_symbols = []
        for syms in sectors.values():
            all_symbols.extend(syms)
            
        loop = asyncio.get_running_loop()
        quotes_list = await loop.run_in_executor(
            None, partial(_market_svc.get_multiple_quotes, all_symbols)
        )
        quotes = {q["symbol"]: q for q in quotes_list}
        
        result = {}
        for sector, syms in sectors.items():
            result[sector] = []
            for sym in syms:
                data = quotes.get(sym, {})
                result[sector].append({"symbol": sym, **data})
                
        return {
            "sectors": result,
            "disclaimer": DISCLAIMER
        }
    except Exception as exc:
        logger.error("Error fetching sectors: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch sectors: {exc}")


@router.post("/sectors/refresh")
async def refresh_sectors() -> dict[str, Any]:
    """Force refresh the market universe sector mapping by scraping Wikipedia.
    
    Returns:
        JSON with the refreshed sector mapping.
    """
    logger.info("POST /market/sectors/refresh")
    try:
        loop = asyncio.get_running_loop()
        new_sectors = await loop.run_in_executor(
            None, _screener_svc.universe_fetcher.refresh_universe_cache
        )
        return {
            "message": "Universe refreshed successfully",
            "sectors": new_sectors
        }
    except Exception as exc:
        logger.error("Error refreshing sectors: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to refresh universe: {exc}")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _safe(row, key: str) -> float | None:
    """Extract a float from a pandas Series, returning None on failure."""
    try:
        import numpy as np

        val = row.get(key)
        if val is None:
            return None
        val = float(val)
        return None if (np.isnan(val) or np.isinf(val)) else round(val, 4)
    except (TypeError, ValueError):
        return None
