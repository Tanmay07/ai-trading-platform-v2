from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
import os

from portfolio_manager import AIPortfolioManager
from portfolio_manager.portfolio_service import PortfolioService

router = APIRouter(tags=["AI Portfolio Manager"])
manager = AIPortfolioManager()
portfolio_service = PortfolioService()

def _get_current_holdings():
    return portfolio_service.get_live_portfolio()

@router.get("/dashboard")
def get_dashboard() -> Dict[str, Any]:
    """Returns the full AI portfolio analysis including dashboard metrics, holdings, and insights."""
    try:
        holdings = _get_current_holdings()
        analysis = manager.analyze_portfolio(holdings)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/what-if")
def simulate_what_if(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates changes to the portfolio."""
    # MVP Implementation: Just return the current analysis + mocked simulation outcome
    try:
        holdings = _get_current_holdings()
        analysis = manager.analyze_portfolio(holdings)
        
        simulation = {
            "original_risk": analysis["dashboard"]["risk_score"],
            "new_risk": analysis["dashboard"]["risk_score"] - 5,
            "original_cagr": analysis["dashboard"]["cagr"],
            "new_cagr": analysis["dashboard"]["cagr"] + 1.5,
            "message": "This change reduces single-stock concentration and improves risk-adjusted returns."
        }
        
        return {"simulation": simulation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
