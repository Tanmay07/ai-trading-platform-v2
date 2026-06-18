"""
Suggestion API Routes

Provides endpoints to fetch pre-computed daily trading suggestions
and real-time full analysis for individual stocks via Jugaad API.
"""

from fastapi import APIRouter, HTTPException
from app.data.s3_service import S3StorageService
from app.data.jugaad_service import JugaadService
from app.utils.logger import get_logger
import yfinance as yf

router = APIRouter()
logger = get_logger(__name__)
s3_service = S3StorageService()
jugaad_service = JugaadService()

SUGGESTIONS_KEY = "daily_suggestions/latest.json"

@router.get("/daily")
async def get_daily_suggestions():
    """
    Fetch all pre-computed daily suggestions for the entire monitored universe.
    """
    try:
        data = s3_service.download_json(SUGGESTIONS_KEY)
        if not data:
            return {"status": "success", "data": {}}
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to fetch daily suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch suggestions")

import math

@router.get("/target-profit")
async def get_target_profit_suggestions(target: float = 5000.0, max_capital: float = None):
    """
    Fetch 2-3 stock suggestions that will yield the `target` profit.
    Calculates the exact quantity to buy based on ML predicted exit prices.
    Filters for solid fundamentals and positive ML forecasts.
    """
    try:
        data = s3_service.download_json(SUGGESTIONS_KEY) or {}
        
        candidates = []
        for symbol, info in data.items():
            trade_setup = info.get("trade_setup", {})
            entry_price = trade_setup.get("sugg_entry")
            exit_price = trade_setup.get("exit_price")
            
            if not entry_price or not exit_price:
                continue
                
            # Filter 1: Must have a positive predicted movement
            profit_per_share = exit_price - entry_price
            if profit_per_share <= 0:
                continue
                
            # Filter 2: Fundamentals check
            # We prefer stocks with positive ROE and EPS
            fundamentals = info.get("fundamentals", {})
            roe = fundamentals.get("roe")
            eps = fundamentals.get("eps")
            
            # Basic sanity check (if data is "N/A" we might skip or penalize)
            if roe not in ("N/A", None) and eps not in ("N/A", None):
                try:
                    if float(roe) <= 0 or float(eps) <= 0:
                        continue
                except (ValueError, TypeError):
                    pass

            # Calculate Quantity and Capital
            # We want: (exit_price - entry_price) * quantity >= target
            quantity = math.ceil(target / profit_per_share)
            capital_required = quantity * entry_price
            
            # Filter 3: Capital Constraint
            if max_capital and capital_required > max_capital:
                continue
                
            # Add to candidates
            info["target_plan"] = {
                "target_profit": target,
                "quantity": quantity,
                "capital_required": round(capital_required, 2),
                "profit_per_share": round(profit_per_share, 2),
                "expected_total_profit": round(quantity * profit_per_share, 2)
            }
            candidates.append(info)
            
        # Sort candidates. Best candidates are those that require the least capital for the same profit
        # Or those with the highest R:R ratio. Let's sort by R:R ratio descending, then capital required ascending.
        candidates.sort(key=lambda x: (
            float(x.get("trade_setup", {}).get("rr_ratio", 0)),
            -x["target_plan"]["capital_required"]
        ), reverse=True)
        
        # Return top 3
        return {"status": "success", "data": candidates[:3]}
        
    except Exception as e:
        logger.error(f"Failed to calculate target profit suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate suggestions")

@router.get("/{symbol}/analysis")
async def get_full_analysis(symbol: str):
    """
    Fetch full analysis dashboard data for a specific stock.
    Merges live quote data from Jugaad with pre-computed daily suggestions.
    """
    try:
        # 1. Fetch live quote and fundamentals using yfinance (fast and reliable)
        live_price = None
        live_fundamentals = {}
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is significantly faster than querying full history
            live_price = round(ticker.fast_info.last_price, 2)
            
            # Fetch fundamentals
            info = ticker.info
            live_fundamentals = {
                "eps": info.get("trailingEps", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "pb_ratio": info.get("priceToBook", "N/A"),
                "debt_equity": info.get("debtToEquity", "N/A"),
                "roe": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
                "free_cash_flow": info.get("freeCashflow", "N/A")
            }
        except Exception as e:
            logger.warning(f"Failed to fetch live data via yfinance for {symbol}: {e}")

        # 2. Fetch pre-computed daily suggestion
        suggestions = s3_service.download_json(SUGGESTIONS_KEY) or {}
        suggestion = suggestions.get(symbol, {})

        if not suggestion:
            # Fallback if the script hasn't run for this stock yet
            return {
                "status": "partial",
                "message": "Daily suggestion not found for this symbol. Try running the daily script.",
                "data": {
                    "symbol": symbol,
                    "company_name": symbol,
                    "live_price": live_price,
                    "live_data_raw": {},
                    "trade_setup": {},
                    "ml_analysis": {},
                    "fundamentals": {},
                    "sentiment": {},
                    "ai_reasoning": "Data not yet generated for this stock."
                }
            }

        # 3. Construct the full analysis response
        current_price = live_price if live_price is not None else suggestion.get('current_price')

        response = {
            "symbol": symbol,
            "company_name": suggestion.get("company_name"),
            "live_price": current_price,
            "live_data_raw": {},  # Removed live quote to prevent hanging
            "trade_setup": suggestion.get("trade_setup"),
            "ml_analysis": suggestion.get("ml_analysis"),
            "fundamentals": live_fundamentals if live_fundamentals else suggestion.get("fundamentals"),
            "sentiment": suggestion.get("sentiment"),
            "ai_reasoning": suggestion.get("ai_reasoning"),
            "updated_at": suggestion.get("updated_at")
        }

        return {"status": "success", "data": response}
    except Exception as e:
        logger.error(f"Failed to fetch full analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis")
