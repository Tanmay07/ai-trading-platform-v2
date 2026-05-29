"""
Prediction API Routes

Provides endpoints for stock predictions — top upside candidates
and per-symbol prediction details.

Phase 1 uses rule-based scoring.  Phase 3 will add ML model predictions.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.strategies.recommendation_engine import RecommendationEngine
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Predictions"])

# Shared engine instance
_engine = RecommendationEngine()


# ------------------------------------------------------------------
# Request Models
# ------------------------------------------------------------------

class StrategyRequest(BaseModel):
    symbols: list[str]


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.get("/top-upside")
async def get_top_upside(
    top_n: int = Query(default=5, ge=1, le=20, description="Number of top stocks to return"),
) -> dict[str, Any]:
    """Get the top stocks predicted to move upward.

    Screens the default watchlist (or a configured list) and returns
    the top *N* stocks ranked by bullish conviction score.

    In **Phase 1** this uses rule-based technical scoring.
    **Phase 3** will integrate ML model predictions for higher accuracy.

    Args:
        top_n: Number of results to return (1–20).

    Returns:
        JSON with ``predictions`` list sorted by upside probability.
    """
    logger.info("GET /predictions/top-upside  top_n=%d", top_n)

    try:
        loop = asyncio.get_running_loop()
        results: list[dict] = await loop.run_in_executor(
            None,
            partial(
                _engine.get_top_upside_stocks,
                symbols=list(settings.DEFAULT_WATCHLIST),
                top_n=top_n,
            ),
        )

        # Enrich with rank and probability-style score
        predictions: list[dict] = []
        for rank, rec in enumerate(results, start=1):
            predictions.append(
                {
                    "rank": rank,
                    "symbol": rec.get("symbol", ""),
                    "action": rec.get("action", "HOLD"),
                    "probability": rec.get("confidence_score", 0.0),
                    "risk_score": rec.get("risk_score", "N/A"),
                    "reasons": rec.get("reasons", [])[:5],  # Top 5 reasons
                    "current_price": rec.get("current_price", 0.0),
                    "suggested_target": rec.get("suggested_target", 0.0),
                    "suggested_stop_loss": rec.get("suggested_stop_loss", 0.0),
                    "time_horizon": rec.get("time_horizon", "N/A"),
                }
            )

        return {
            "predictions": predictions,
            "count": len(predictions),
            "model_type": "rule-based (Phase 1)",
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error generating top-upside predictions: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate predictions: {exc}"
        )


@router.get("/{symbol}")
async def get_prediction(symbol: str) -> dict[str, Any]:
    """Get a detailed prediction / recommendation for a specific symbol.

    Returns a full recommendation including action, confidence, risk,
    supporting indicators, stop-loss, and target price.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE`` or ``RELIANCE.NS``).

    Returns:
        JSON with the complete recommendation object.
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /predictions/%s", symbol)

    try:
        loop = asyncio.get_running_loop()
        recommendation: dict = await loop.run_in_executor(
            None, partial(_engine.get_recommendation, symbol)
        )

        return {
            "prediction": recommendation,
            "model_type": "rule-based (Phase 1)",
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error generating prediction for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate prediction: {exc}"
        )


@router.post("/strategy")
async def get_strategy(request: StrategyRequest) -> dict[str, Any]:
    """Get recommendations for a batch of symbols (e.g. from a sector).

    Returns:
        JSON with a list of complete recommendation objects.
    """
    symbols = request.symbols
    logger.info("POST /predictions/strategy for %d symbols", len(symbols))

    try:
        loop = asyncio.get_running_loop()
        recommendations: list[dict] = await loop.run_in_executor(
            None, partial(_engine.get_watchlist_recommendations, symbols)
        )

        return {
            "predictions": recommendations,
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error generating strategy predictions: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate predictions: {exc}"
        )
