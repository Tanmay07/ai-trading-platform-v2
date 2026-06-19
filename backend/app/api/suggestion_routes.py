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
    Fetch 3 bundle suggestions that will collectively yield the `target` profit.
    Finds pairs of high-quality stocks and evenly distributes the profit target among them.
    Filters for solid fundamentals and positive ML forecasts.
    """
    try:
        data = s3_service.download_json(SUGGESTIONS_KEY) or {}
        
        # 1. Filter for top-quality individual candidates
        valid_stocks = []
        for symbol, info in data.items():
            trade_setup = info.get("trade_setup", {})
            current_price = info.get("current_price")
            
            # Use current price as entry price. Fallback to sugg_entry if current_price is missing.
            entry_price = current_price if current_price else trade_setup.get("sugg_entry")
            exit_price = trade_setup.get("exit_price")
            
            if current_price:
                trade_setup["sugg_entry"] = current_price
            
            if not entry_price or not exit_price:
                continue
                
            profit_per_share = exit_price - entry_price
            if profit_per_share <= 0:
                continue
                
            fundamentals = info.get("fundamentals", {})
            roe = fundamentals.get("roe")
            eps = fundamentals.get("eps")
            
            if roe not in ("N/A", None) and eps not in ("N/A", None):
                try:
                    if float(roe) <= 0 or float(eps) <= 0:
                        continue
                except (ValueError, TypeError):
                    pass
            
            # Store necessary info for bundle generation
            info["_profit_per_share"] = profit_per_share
            info["_entry_price"] = entry_price
            info["_rr_ratio"] = float(trade_setup.get("rr_ratio", 0))
            
            # Extract ML metrics for growth potential
            ml = info.get("ml_analysis", {})
            info["_forecast_value"] = float(ml.get("forecast_value", 0))
            
            # Confidence is like "78.2%", strip the % and convert to float
            conf_str = ml.get("model_confidence", "0").replace("%", "")
            try:
                info["_confidence"] = float(conf_str)
            except ValueError:
                info["_confidence"] = 0.0

            valid_stocks.append(info)
            
        # Sort by Forecast Value (Growth) and Model Confidence to maximize short-term gains
        valid_stocks.sort(key=lambda x: (x["_forecast_value"], x["_confidence"]), reverse=True)
        # Take the top 20 candidates to form bundles from
        top_candidates = valid_stocks[:20]
        
        # 2. Generate bundles of 2 stocks
        bundles = []
        import itertools
        import uuid
        
        target_min = target * 0.9
        target_max = target * 1.1
        
        for stock_a, stock_b in itertools.combinations(top_candidates, 2):
            # Split target equally
            target_per_stock = target / 2.0
            
            qty_a = math.ceil(target_per_stock / stock_a["_profit_per_share"])
            qty_b = math.ceil(target_per_stock / stock_b["_profit_per_share"])
            
            capital_a = qty_a * stock_a["_entry_price"]
            capital_b = qty_b * stock_b["_entry_price"]
            total_capital = capital_a + capital_b
            
            if max_capital and total_capital > max_capital:
                continue
                
            profit_a = qty_a * stock_a["_profit_per_share"]
            profit_b = qty_b * stock_b["_profit_per_share"]
            total_profit = profit_a + profit_b
            
            if target_min <= total_profit <= target_max:
                # Build the bundle object
                # Deep copy to avoid mutating the shared candidate dictionary
                import copy
                s_a = copy.deepcopy(stock_a)
                s_b = copy.deepcopy(stock_b)
                
                # Remove temporary calculation keys
                for key in ["_profit_per_share", "_entry_price", "_rr_ratio"]:
                    s_a.pop(key, None)
                    s_b.pop(key, None)
                
                s_a["target_plan"] = {
                    "quantity": qty_a,
                    "capital_required": round(capital_a, 2),
                    "profit_per_share": round(profit_a / qty_a, 2) if qty_a else 0,
                    "expected_total_profit": round(profit_a, 2)
                }
                
                s_b["target_plan"] = {
                    "quantity": qty_b,
                    "capital_required": round(capital_b, 2),
                    "profit_per_share": round(profit_b / qty_b, 2) if qty_b else 0,
                    "expected_total_profit": round(profit_b, 2)
                }
                
                bundles.append({
                    "bundle_id": str(uuid.uuid4()),
                    "total_capital_required": round(total_capital, 2),
                    "expected_total_profit": round(total_profit, 2),
                    "combined_growth_forecast": round((stock_a["_forecast_value"] + stock_b["_forecast_value"]) / 2, 2),
                    "combined_confidence": round((stock_a["_confidence"] + stock_b["_confidence"]) / 2, 2),
                    "stocks": [s_a, s_b]
                })

        # Sort bundles: prioritize highest growth forecast, then confidence, then lowest capital required
        bundles.sort(key=lambda b: (b["combined_growth_forecast"], b["combined_confidence"], -b["total_capital_required"]), reverse=True)
        
        # Return top 3 bundles
        return {"status": "success", "data": bundles[:3]}
        
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
