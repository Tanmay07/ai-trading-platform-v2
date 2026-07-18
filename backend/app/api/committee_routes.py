from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import random

from committee.engine.investment_committee import InvestmentCommittee

router = APIRouter(tags=["committee"])

class TradeContextRequest(BaseModel):
    symbol: str
    prediction: Dict[str, Any]
    portfolio: Dict[str, Any]
    execution: Dict[str, Any]

@router.post("/evaluate")
def evaluate_trade(req: TradeContextRequest):
    """
    Evaluates a specific trade through the Investment Committee.
    """
    try:
        engine = InvestmentCommittee()
        # Convert pydantic model to dict
        context = req.dict()
        result = engine.evaluate_trade(context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mock")
def get_mock_evaluations():
    """
    Returns mocked committee evaluations for testing the UI.
    """
    try:
        engine = InvestmentCommittee()
        results = []
        
        symbols = ["TCS.NS", "HDFCBANK.NS", "RELIANCE.NS"]
        for sym in symbols:
            mock_context = {
                "symbol": sym,
                "prediction": {
                    "trade_quality": random.uniform(50, 95),
                    "confidence": random.uniform(60, 99)
                },
                "portfolio": {
                    "is_rejected": random.choice([True, False, False]), # 33% chance of portfolio veto
                    "portfolio_health": random.uniform(60, 95)
                },
                "execution": {
                    "risk_reward": random.uniform(1.5, 4.0),
                    "risk_status": "PASSED"
                }
            }
            results.append(engine.evaluate_trade(mock_context))
            
        return {"evaluations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
