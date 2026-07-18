from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import time

from paper_trading.engine.paper_trading_engine import PaperTradingEngine
from paper_trading.attribution.attribution_engine import AttributionEngine

router = APIRouter(tags=["paper_trading"])

# Global instance for simulation state persistence across API calls
attribution_engine = AttributionEngine()
engine = PaperTradingEngine(attribution_engine=attribution_engine)

@router.post("/simulate")
def run_simulation():
    """
    Runs a mock simulation: 
    1. Injects committee recommendations
    2. Ticks the market a few times
    3. Triggers exits
    4. Returns the final portfolio state and journal.
    """
    try:
        # Reset engine for clean simulation
        global engine, attribution_engine
        attribution_engine = AttributionEngine()
        engine = PaperTradingEngine(attribution_engine=attribution_engine)
        
        # 1. Inject Committee BUY recommendations
        mock_recs = [
            {
                "symbol": "TCS.NS",
                "final_decision": "BUY",
                "context_snapshot": {
                    "execution": {"entry_price": 4000.0, "capital_allocated": 100000.0, "stop_loss": 3800.0, "target_1": 4400.0, "holding_period": 10},
                    "prediction": {"confidence": 92}
                }
            },
            {
                "symbol": "HDFCBANK.NS",
                "final_decision": "BUY",
                "context_snapshot": {
                    "execution": {"entry_price": 1600.0, "capital_allocated": 100000.0, "stop_loss": 1550.0, "target_1": 1700.0, "holding_period": 5},
                    "prediction": {"confidence": 75}
                }
            }
        ]
        
        for rec in mock_recs:
            engine.execute_committee_recommendation(rec)
            
        # 2. Tick 1 (Prices move up slightly)
        engine.process_market_tick({"TCS.NS": 4100.0, "HDFCBANK.NS": 1620.0})
        
        # 3. Tick 2 (HDFCBANK hits stop loss, TCS hits target)
        engine.process_market_tick({"TCS.NS": 4450.0, "HDFCBANK.NS": 1540.0})
        
        return {
            "portfolio_summary": engine.portfolio.get_summary(),
            "open_positions": engine.portfolio.open_positions,
            "closed_trades": engine.portfolio.closed_positions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
