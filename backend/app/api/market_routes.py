from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import date
from market_data.service import MarketDataService

router = APIRouter(tags=["Market Data Platform"])
market_service = MarketDataService()

@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    """Get the live/latest quote for a single symbol."""
    try:
        quote = market_service.get_live_quote(symbol)
        return quote.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quotes")
def get_quotes(symbols: str = Query(..., description="Comma separated list of symbols")):
    """Get batch quotes for multiple symbols."""
    try:
        sym_list = [s.strip() for s in symbols.split(",")]
        quotes = market_service.get_live_quotes(sym_list)
        return {k: v.model_dump() for k, v in quotes.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{symbol}")
def get_history(symbol: str, start_date: date, end_date: date):
    """Get historical OHLCV data."""
    try:
        data = market_service.get_historical_data(symbol, start_date, end_date)
        return [c.model_dump() for c in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_market_status():
    """Get the current state of the market (Open, Closed, Holiday)."""
    try:
        status = market_service.get_market_status()
        return status.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
