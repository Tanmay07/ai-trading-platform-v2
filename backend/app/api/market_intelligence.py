from fastapi import APIRouter, HTTPException
from app.services.market_intelligence_orchestrator import MarketIntelligenceOrchestrator
from typing import Dict, Any

router = APIRouter(prefix="/api/market-intelligence", tags=["Market Intelligence"])

@router.get("/")
def get_market_intelligence() -> Dict[str, Any]:
    try:
        orchestrator = MarketIntelligenceOrchestrator()
        
        # We need Nifty 50 and Universe.
        # Since this is a standalone API, we'll fetch just Nifty 50.
        import yfinance as yf
        import pandas as pd
        df_market = yf.download("^NSEI", period="1y", interval="1d", progress=False)
        
        # We mock an empty universe df here since fetching all 500 takes 10s and we just want quick API
        # To get breadth, one could optionally fetch the universe, but for standalone it's too heavy.
        df_empty = pd.DataFrame()
        
        results = orchestrator.analyze_market(df_market, df_empty)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
