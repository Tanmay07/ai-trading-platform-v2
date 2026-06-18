"""
Daily Suggestion Engine

Runs after market hours to generate full AI trading suggestions
using Jugaad NSE historical data and basic ML logic.
Saves the results to S3 for the Full Analysis Dashboard.
"""

import sys
import os
import json
import threading
import concurrent.futures
from datetime import date, timedelta
import pandas as pd
import yfinance as yf

# Ensure the app module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data.jugaad_service import JugaadService
from app.data.universe_fetcher import UniverseFetcherService
from app.data.s3_service import S3StorageService
from app.utils.logger import get_logger

logger = get_logger("daily_suggestion_job")

SUGGESTIONS_KEY = "daily_suggestions/latest.json"

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def generate_mock_ai_reasoning(symbol, technicals, sentiment) -> str:
    """Mock Google Gemini AI logic for trend reasoning."""
    if technicals['Close'] > technicals['SMA_20']:
        trend = "upward"
        prob = 75.4
    else:
        trend = "downward"
        prob = 62.1
        
    return f"AI predicts a {prob}% probability of an {trend} trend because the stock is in a clear positive momentum, revenue growth is solid, and the company has healthy return on equity."

def run_daily_job():
    logger.info("Starting daily suggestion generation job...")
    s3_service = S3StorageService()
    jugaad_service = JugaadService()
    universe_fetcher = UniverseFetcherService()

    # Use NIFTY 50 as the base universe for the daily suggestions
    # In a real scenario, this could be the entire NSE universe using Bhavcopy
    try:
        sector_map = universe_fetcher.refresh_universe_cache()
    except Exception as e:
        logger.error(f"Failed to fetch universe: {e}")
        return

    all_symbols = []
    for sector, symbols in sector_map.items():
        all_symbols.extend(symbols)

    to_date = date.today()
    from_date = to_date - timedelta(days=90) # 3 months of data for indicators

    suggestions = {}
    suggestions_lock = threading.Lock()

    def process_symbol(symbol):
        # 1. Fetch Historical Data from Jugaad
        df = jugaad_service.get_historical_data(symbol, from_date, to_date)
        if df.empty or len(df) < 20:
            logger.warning(f"Insufficient historical data for {symbol}")
            return
            
        current_price = df['Close'].iloc[-1]
        
        # 2. Calculate Technicals
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['ATR'] = calculate_atr(df)
        atr_val = df['ATR'].iloc[-1]
        
        # 3. Trade Setup Logic
        entry_price = round(current_price * 0.99, 2)
        stop_loss = round(current_price - (1.5 * atr_val), 2)
        exit_price = round(current_price + (3.0 * atr_val), 2)
        risk = entry_price - stop_loss
        reward = exit_price - entry_price
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0

        # 4. Fetch Fundamentals via yfinance
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            fundamentals = {
                "eps": info.get("trailingEps", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "pb_ratio": info.get("priceToBook", "N/A"),
                "debt_equity": info.get("debtToEquity", "N/A"),
                "roe": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
                "free_cash_flow": info.get("freeCashflow", "N/A")
            }
        except Exception:
            fundamentals = {}
            info = {}

        # 5. Mock Deep ML Analysis
        ml_analysis = {
            "3_day_forecast": "+1.44%",
            "signal_strength": "37.9%",
            "model_confidence": "78.2%",
            "forecast_value": 1.44
        }
        
        # 6. Sentiment Mock
        sentiment = {
            "news_sentiment": "Bullish",
            "market_sentiment": "Neutral Market",
            "score": "60/100"
        }

        # 7. AI Trend Reasoning
        technicals = {
            "Close": current_price,
            "SMA_20": df['SMA_20'].iloc[-1]
        }
        ai_reasoning = generate_mock_ai_reasoning(symbol, technicals, sentiment)

        company_name = info.get("shortName", symbol.replace(".NS", ""))
        
        with suggestions_lock:
            suggestions[symbol] = {
                "symbol": symbol,
                "company_name": company_name,
                "current_price": current_price,
                "trade_setup": {
                    "sugg_entry": entry_price,
                    "exit_price": exit_price,
                    "stop_loss": stop_loss,
                    "rr_ratio": rr_ratio
                },
                "ml_analysis": ml_analysis,
                "fundamentals": fundamentals,
                "sentiment": sentiment,
                "ai_reasoning": ai_reasoning,
                "updated_at": to_date.isoformat()
            }
        logger.info(f"Successfully processed {symbol}")

    logger.info(f"Starting ThreadPoolExecutor for {len(all_symbols)} symbols...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_symbol, all_symbols)

    # Save to S3
    logger.info(f"Saving {len(suggestions)} suggestions to S3.")
    s3_service.upload_json(SUGGESTIONS_KEY, suggestions)
    logger.info("Daily suggestion job completed successfully.")

if __name__ == "__main__":
    run_daily_job()
