"""
ML API Routes — Phase 3

Provides endpoints for ML model training, prediction, and status.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.ml.model_manager import ModelManager
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["ML"])

_manager = ModelManager()


# ------------------------------------------------------------------
# Training endpoints
# ------------------------------------------------------------------


@router.post("/train/{symbol}")
async def train_model(
    symbol: str,
    period: str = Query(
        default="2y", description="History period for training (e.g. 1y, 2y, 5y)"
    ),
) -> dict[str, Any]:
    """Train ML models for a specific stock symbol.

    Trains XGBoost, LightGBM, and an ensemble model, evaluates each
    on a held-out test set, and saves the best one.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE``).
        period: History period for training data.

    Returns:
        JSON with training metrics, feature importance, and model info.
    """
    symbol = validate_symbol(symbol)
    logger.info("POST /ml/train/%s (period=%s)", symbol, period)

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            partial(_manager.train_model, symbol, period),
        )

        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Training failed: {result.error}",
            )

        return {
            "status": "success",
            "training_result": result.to_dict(),
            "disclaimer": DISCLAIMER,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ML training failed for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {exc}",
        )


@router.post("/train-all")
async def train_all_models(
    period: str = Query(
        default="2y", description="History period for training"
    ),
    top_n: int = Query(
        default=10, ge=1, le=20, description="Number of stocks from watchlist"
    ),
) -> dict[str, Any]:
    """Train ML models for the entire watchlist (or top N stocks).

    Args:
        period: History period for training data.
        top_n: Number of stocks from the default watchlist.

    Returns:
        JSON with per-stock training results summary.
    """
    symbols = list(settings.DEFAULT_WATCHLIST)[:top_n]
    logger.info("POST /ml/train-all (period=%s, stocks=%d)", period, len(symbols))

    try:
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            partial(_manager.train_all, symbols, period),
        )

        summary = {
            "total": len(results),
            "success": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
        }

        return {
            "status": "complete",
            "summary": summary,
            "results": [r.to_dict() for r in results],
            "disclaimer": DISCLAIMER,
        }

    except Exception as exc:
        logger.error("Batch training failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch training failed: {exc}",
        )


# ------------------------------------------------------------------
# Prediction endpoints
# ------------------------------------------------------------------


@router.get("/predict/{symbol}")
async def predict(symbol: str) -> dict[str, Any]:
    """Get ML prediction for a stock symbol.

    Uses the best trained model for the symbol. If no model has been
    trained yet, returns a 404.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE``).

    Returns:
        JSON with predicted direction, probability, and confidence.
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /ml/predict/%s", symbol)

    try:
        loop = asyncio.get_running_loop()
        prediction = await loop.run_in_executor(
            None,
            partial(_manager.predict, symbol),
        )

        if prediction is None:
            raise HTTPException(
                status_code=404,
                detail=f"No trained model found for {symbol}. "
                       f"Train one first via POST /ml/train/{symbol}",
            )

        return {
            "symbol": symbol,
            "prediction": prediction.to_dict(),
            "needs_retrain": _manager.needs_retrain(symbol),
            "disclaimer": DISCLAIMER,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ML prediction failed for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )


# ------------------------------------------------------------------
# Status endpoints
# ------------------------------------------------------------------


@router.get("/status/{symbol}")
async def get_model_status(symbol: str) -> dict[str, Any]:
    """Get training status and metadata for a symbol's model.

    Args:
        symbol: NSE stock symbol.

    Returns:
        JSON with model metadata, or 404 if no model exists.
    """
    symbol = validate_symbol(symbol)
    info = _manager.get_model_info(symbol)

    if info is None:
        raise HTTPException(
            status_code=404,
            detail=f"No trained model found for {symbol}",
        )

    return {
        "symbol": symbol,
        "model_info": info,
        "needs_retrain": _manager.needs_retrain(symbol),
        "disclaimer": DISCLAIMER,
    }


@router.get("/status")
async def get_all_model_status() -> dict[str, Any]:
    """Get training status for all trained models.

    Returns:
        JSON with list of model metadata for all symbols that have
        trained models.
    """
    all_info = _manager.get_all_model_info()

    return {
        "models_count": len(all_info),
        "models": all_info,
        "disclaimer": DISCLAIMER,
    }
