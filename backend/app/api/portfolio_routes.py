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
from app.data.market_data_service import MarketDataService
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Portfolio"])

# Shared service instances
_portfolio_svc = PortfolioService()
_recommendation_engine = RecommendationEngine()
_market_data = MarketDataService()


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


class UpdateHoldingRequest(BaseModel):
    """Request body for updating an existing portfolio holding."""

    quantity: int = Field(..., gt=0, description="New number of shares")
    buy_price: float = Field(..., gt=0, description="New average purchase price (INR)")
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


@router.put("/{symbol}")
async def update_holding(
    symbol: str,
    request: UpdateHoldingRequest,
) -> dict[str, Any]:
    """Update an existing holding in the portfolio.
    
    This overwrites the quantity and average buy price explicitly.
    """
    symbol = validate_symbol(symbol)
    logger.info(
        "PUT /portfolio/%s — qty=%d price=%.2f",
        symbol,
        request.quantity,
        request.buy_price,
    )

    try:
        holding = _portfolio_svc.update_holding(
            symbol=symbol,
            quantity=request.quantity,
            buy_price=request.buy_price,
            sector=request.sector,
            notes=request.notes,
        )

        return {
            "message": "Holding updated successfully",
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
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("Error updating holding: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update holding: {exc}")


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


@router.get("/full-analysis")
async def get_full_analysis() -> dict[str, Any]:
    """Get a comprehensive portfolio analysis with verdict and rationale for every holding.

    Combines live portfolio data (invested value, current value, weight %)
    with the strict recommendation engine to produce a spreadsheet-style analysis.
    """
    logger.info("GET /portfolio/full-analysis")

    try:
        loop = asyncio.get_running_loop()
        summary: dict = await loop.run_in_executor(
            None, partial(_portfolio_svc.get_portfolio_summary)
        )

        holdings = summary.get("holdings", [])
        if not holdings:
            return {
                "analysis": [],
                "totals": {
                    "total_invested": 0.0,
                    "total_market_value": 0.0,
                    "total_unrealized_pnl": 0.0,
                    "total_unrealized_pnl_pct": 0.0,
                },
                "disclaimer": DISCLAIMER,
            }

        total_market_value = summary.get("total_market_value", 0.0)

        # Build holdings context for the recommendation engine
        holdings_data = [
            {
                "symbol": h["symbol"],
                "quantity": h["quantity"],
                "avg_buy_price": h["avg_buy_price"],
                "current_price": h.get("current_price"),
            }
            for h in holdings
        ]

        recommendations: list[dict] = await loop.run_in_executor(
            None,
            partial(_recommendation_engine.get_portfolio_recommendations, holdings_data),
        )

        # Build a lookup map: symbol -> recommendation
        rec_map = {r["symbol"]: r for r in recommendations}

        # Fetch sector info for all holdings
        def _fetch_sectors(syms: list[str]) -> dict[str, str]:
            result = {}
            for s in syms:
                try:
                    info = _market_data.get_stock_info(s)
                    sector = info.get("sector", "") or info.get("industry", "")
                    result[s] = sector if sector else "N/A"
                except Exception:
                    result[s] = "N/A"
            return result

        all_symbols = [h["symbol"] for h in holdings]
        sector_map: dict[str, str] = await loop.run_in_executor(
            None, partial(_fetch_sectors, all_symbols)
        )

        analysis_rows: list[dict] = []
        for h in holdings:
            symbol = h["symbol"]
            qty = h["quantity"]
            avg_price = h["avg_buy_price"]
            current_price = h.get("current_price", avg_price)
            invested_value = round(avg_price * qty, 2)
            current_value = round(current_price * qty, 2)
            weight_pct = round((current_value / total_market_value * 100), 2) if total_market_value > 0 else 0.0
            pnl_pct = h.get("unrealized_pnl_pct", 0.0)
            sector = sector_map.get(symbol, "N/A")

            rec = rec_map.get(symbol, {})
            verdict = rec.get("action", "HOLD")

            # Generate a concise rationale string focused on stock potential
            rationale = _generate_rationale(
                symbol=symbol,
                verdict=verdict,
                pnl_pct=pnl_pct,
                current_price=current_price,
                avg_price=avg_price,
                sector=sector,
                hold_target=rec.get("hold_target"),
                suggested_target=rec.get("suggested_target"),
                suggested_stop_loss=rec.get("suggested_stop_loss"),
                confidence=rec.get("confidence_score", 0.0),
            )

            analysis_rows.append({
                "symbol": symbol,
                "sector": sector,
                "quantity": qty,
                "avg_price": avg_price,
                "ltp": current_price,
                "invested_value": invested_value,
                "current_value": current_value,
                "weight_pct": weight_pct,
                "pnl_pct": pnl_pct,
                "verdict": verdict,
                "rationale": rationale,
                "hold_target": rec.get("hold_target"),
                "suggested_target": rec.get("suggested_target"),
                "suggested_stop_loss": rec.get("suggested_stop_loss"),
                "confidence_score": rec.get("confidence_score", 0.0),
            })

        # Sort: BUY MORE first, then AVERAGE DOWN, then HOLD, then SELL/CUT LOSSES
        verdict_order = {"BUY MORE": 0, "AVERAGE DOWN": 1, "BUY": 2, "HOLD": 3, "SELL": 4, "CUT LOSSES": 5, "SELL/TRIM": 6}
        analysis_rows.sort(key=lambda r: (verdict_order.get(r["verdict"], 99), -abs(r["pnl_pct"])))

        return {
            "analysis": analysis_rows,
            "totals": {
                "total_invested": summary.get("total_invested", 0.0),
                "total_market_value": total_market_value,
                "total_unrealized_pnl": summary.get("total_unrealized_pnl", 0.0),
                "total_unrealized_pnl_pct": summary.get("total_unrealized_pnl_pct", 0.0),
            },
            "holdings_count": len(analysis_rows),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error generating full analysis: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate full analysis: {exc}"
        )


def _generate_rationale(
    symbol: str,
    verdict: str,
    pnl_pct: float,
    current_price: float,
    avg_price: float,
    sector: str,
    hold_target: float | None,
    suggested_target: float | None,
    suggested_stop_loss: float | None,
    confidence: float,
) -> str:
    """Generate a concise, spreadsheet-style rationale based on stock potential.
    
    Does NOT judge by position size — focuses purely on technical/fundamental merit.
    """
    pnl_str = f"{pnl_pct:+.1f}%"
    target_str = f", target ₹{suggested_target:.2f}" if suggested_target else ""
    sl_str = f", stop-loss ₹{suggested_stop_loss:.2f}" if suggested_stop_loss else ""

    if verdict == "BUY MORE":
        return f"Strong gain ({pnl_str}) with bullish continuation signals — consider scaling position size with real conviction{target_str}"
    elif verdict == "AVERAGE DOWN":
        return f"Underwater ({pnl_str}) but showing strong technical reversal/bullish signals. Optimal zone to average down and lower your cost basis{target_str}"
    elif verdict == "CUT LOSSES":
        if pnl_pct < -30:
            return f"Down {abs(pnl_pct):.0f}% — technicals completely broken, trend reversed with no recovery catalyst visible. Exit and reallocate capital{sl_str}"
        else:
            return f"Down {abs(pnl_pct):.0f}% — bearish momentum persisting, low probability of recovery to cost basis. Cut losses to preserve capital{sl_str}"
    elif verdict == "SELL":
        if pnl_pct < -15:
            return f"Down {abs(pnl_pct):.0f}% — weakening technicals and fading momentum. Sell to redeploy capital into higher-conviction setups{sl_str}"
        elif pnl_pct < 0:
            return f"Slightly underwater ({pnl_str}) — no bullish catalyst on the horizon. Consider exiting to avoid further erosion{sl_str}"
        else:
            return f"In profit ({pnl_str}) but momentum is fading — consider booking profits before reversal{sl_str}"
    elif verdict == "HOLD":
        # ETF-specific rationale
        if "ETF" in symbol.upper() or "BEES" in symbol.upper():
            if "GOLD" in symbol.upper():
                return "Gold ETF — hedge allocation working as intended"
            elif "SILV" in symbol.upper():
                return "Silver ETF — commodity hedge, hold for diversification"
            elif "LIQUID" in symbol.upper():
                return "Liquid fund — parked cash/emergency buffer, not equity risk"
            elif "NIFTY" in symbol.upper() or "JUNIOR" in symbol.upper():
                return "Passive core (Nifty 50 / Next 50) — portfolio anchor, no action needed"
            else:
                return "ETF — systematic allocation, hold as intended"
        # Equity HOLD
        if hold_target:
            if pnl_pct > 5:
                return f"Profitable ({pnl_str}), let it run — hold until ₹{hold_target:.2f} before re-evaluating"
            elif pnl_pct > 0:
                return f"Slight gain ({pnl_str}), forming base — hold until ₹{hold_target:.2f} target"
            else:
                return f"Underwater ({pnl_str}) but technicals are stabilizing — hold until ₹{hold_target:.2f}, review on quarterly results"
        if pnl_pct > 10:
            return f"Strong gain ({pnl_str}), momentum intact — let it run, review on quarterly results"
        elif pnl_pct > 0:
            return f"Slight gain ({pnl_str}), range-bound — monitor, no urgent action needed"
        elif pnl_pct > -5:
            return f"Small drawdown ({pnl_str}), consolidating — monitor for breakout or breakdown"
        else:
            return f"Underwater ({pnl_str}) but technicals are neutral — hold and watch for recovery signals"
    else:
        return f"Engine verdict: {verdict} — review manually"
