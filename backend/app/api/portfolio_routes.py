from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import random

from portfolio.engine.portfolio_builder import PortfolioBuilder

router = APIRouter(tags=["portfolio"])

class PortfolioRequest(BaseModel):
    available_cash: float = 100000.0
    
class AnalyzeRequest(BaseModel):
    current_holdings: List[Dict[str, Any]]

# Mock generator for candidates (in a real system this queries PredictionService for the top N ranking)
def _generate_mock_candidates(n=50) -> List[Dict[str, Any]]:
    sectors = ["Financials", "Technology", "Healthcare", "Energy", "Consumer", "Industrials"]
    candidates = []
    for i in range(n):
        # Biased somewhat towards Financials to test sector constraints
        sector = random.choice(sectors + ["Financials", "Financials"]) 
        tq = random.uniform(50, 95)
        cp = random.uniform(0.6, 0.99)
        candidates.append({
            "symbol": f"MOCK_{i}",
            "sector": sector,
            "trade_quality_prediction": tq,
            "classification_probability": cp,
            "expected_return": random.uniform(2, 12)
        })
    return candidates


@router.post("/build")
def build_portfolio(req: PortfolioRequest):
    """
    Builds an optimal portfolio from candidate opportunities.
    """
    try:
        builder = PortfolioBuilder()
        # In a real system, we fetch predictions from PredictionService
        # Here we mock 50 highly rated candidates
        candidates = _generate_mock_candidates(50)
        
        proposal = builder.build_proposed_portfolio(candidates, req.available_cash)
        return proposal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
def analyze_portfolio(req: AnalyzeRequest):
    """
    Analyzes an existing portfolio and returns recommendations.
    """
    try:
        builder = PortfolioBuilder()
        # Mock predictions lookup for the current holdings
        predictions = {h['symbol']: {"trade_quality_prediction": random.uniform(30, 90)} for h in req.current_holdings}
        
        recommendations = builder.analyze_existing_portfolio(req.current_holdings, predictions)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
