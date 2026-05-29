"""
Portfolio API Routes

Provides endpoints for managing portfolio holdings, viewing P&L,
and getting BUY/SELL/HOLD recommendations for portfolio stocks.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.portfolio.portfolio_service import PortfolioService
from app.strategies.recommendation_engine import RecommendationEngine
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Portfolio"])

# Shared service instances
_portfolio_svc = PortfolioService()
_recommendation_engine = RecommendationEngine()


# ------------------------------------------------------------------
# Pydantic request / response models
# ------------------------------------------------------------------


class AddHoldingRequest(BaseModel):
    """Request body for adding a portfolio holding."""

    symbol: str = Field(..., description="NSE stock symbol (e.g. RELIANCE or RELIANCE.NS)")
    quantity: int = Field(..., gt=0, description="Number of shares to buy")
    buy_price: float = Field(..., gt=0, description="Purchase price per share (INR)")
    sector: str | None = Field(None, description="Sector classification")
    notes: str | None = Field(None, description="Optional notes")


class HoldingResponse(BaseModel):
    """Serialised portfolio holding."""

    symbol: str
    quantity: int
    avg_buy_price: float
    sector: str | None = None
    notes: str | None = None
    message: str = "Holding added/updated successfully"
    disclaimer: str = DISCLAIMER


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.post("")
async def add_holding(
    request: AddHoldingRequest,
) -> dict[str, Any]:
    """Add a holding to the portfolio.

    If the symbol already exists, the quantity is incremented and the
    buy price is recalculated as a weighted average.
    """
    logger.info(
        "POST /portfolio — symbol=%s qty=%d price=%.2f",
        request.symbol,
        request.quantity,
        request.buy_price,
    )

    try:
        holding = _portfolio_svc.add_holding(
            symbol=request.symbol,
            quantity=request.quantity,
            buy_price=request.buy_price,
            sector=request.sector,
            notes=request.notes,
        )

        return {
            "message": "Holding added/updated successfully",
            "holding": {
                "symbol": holding["symbol"],
                "quantity": holding["quantity"],
                "avg_buy_price": holding["avg_buy_price"],
                "sector": holding.get("sector"),
                "notes": holding.get("notes"),
            },
            "disclaimer": DISCLAIMER,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Error adding holding: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add holding: {exc}")


@router.get("")
async def get_portfolio() -> dict[str, Any]:
    """Get portfolio summary with live prices and unrealized P&L.

    Fetches current market prices for each holding and calculates
    market value, unrealized gains/losses, and overall portfolio metrics.
    """
    logger.info("GET /portfolio")

    try:
        loop = asyncio.get_running_loop()
        summary: dict = await loop.run_in_executor(
            None, partial(_portfolio_svc.get_portfolio_summary)
        )
        return summary
    except Exception as exc:
        logger.error("Error fetching portfolio: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {exc}")


@router.delete("/{symbol}")
async def remove_holding(
    symbol: str,
) -> dict[str, Any]:
    """Remove a holding from the portfolio.

    Records a SELL transaction at the average buy price (paper-trade).
    """
    symbol = validate_symbol(symbol)
    logger.info("DELETE /portfolio/%s", symbol)

    try:
        removed = _portfolio_svc.remove_holding(symbol)
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"Holding {symbol} not found in portfolio",
            )

        return {
            "message": f"Holding {symbol} removed successfully",
            "symbol": symbol,
            "disclaimer": DISCLAIMER,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error removing holding %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to remove holding: {exc}")


@router.get("/recommendations")
async def get_recommendations() -> dict[str, Any]:
    """Get BUY/SELL/HOLD recommendations for all portfolio stocks.

    Runs the recommendation engine on each holding, combining
    technical analysis, risk assessment, and market context.
    """
    logger.info("GET /portfolio/recommendations")

    try:
        holdings = _portfolio_svc.get_holdings()

        if not holdings:
            return {
                "recommendations": [],
                "count": 0,
                "message": "No holdings in portfolio. Add stocks to get recommendations.",
                "disclaimer": DISCLAIMER,
            }

        # Build holdings list for the recommendation engine
        holdings_data = [
            {
                "symbol": h["symbol"],
                "quantity": h["quantity"],
                "avg_buy_price": h["avg_buy_price"],
                "sector": h.get("sector"),
            }
            for h in holdings
        ]

        loop = asyncio.get_running_loop()
        recommendations: list[dict] = await loop.run_in_executor(
            None,
            partial(_recommendation_engine.get_portfolio_recommendations, holdings_data),
        )

        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error generating recommendations: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate recommendations: {exc}"
        )
