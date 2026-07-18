from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from market_regime.detection.ensemble_detector import EnsembleDetector
from market_regime.digital_twin.market_digital_twin import MarketDigitalTwin
from market_regime.adaptation.strategy_allocator import StrategyAllocator
from market_regime.adaptation.risk_adjuster import RiskAdjuster

router = APIRouter(tags=["market_regime"])

detector = EnsembleDetector()
twin = MarketDigitalTwin()
allocator = StrategyAllocator()
risk = RiskAdjuster()

@router.get("/current")
def get_current_regime():
    """
    Returns the current detected market regime and confidence.
    """
    try:
        return detector.detect_current_regime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_regime_history(days: int = 365):
    """
    Returns historical regime states.
    """
    try:
        return {"history": detector.detect_historical_regimes(days)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/digital_twin")
def get_digital_twin_forecast():
    """
    Simulates future market paths and transitions.
    """
    try:
        current = detector.detect_current_regime()["regime"]
        return twin.simulate_future_paths(current)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
def get_regime_recommendations():
    """
    Returns optimal strategy allocation and risk budgets for the current regime and twin forecast.
    """
    try:
        current = detector.detect_current_regime()["regime"]
        forecasts = twin.simulate_future_paths(current)["projections"]
        
        strategy_alloc = allocator.recommend_allocation(current, forecasts)
        risk_budgets = risk.calculate_risk_budgets(current, forecasts)
        
        return {
            "current_regime": current,
            "strategy_recommendation": strategy_alloc,
            "risk_recommendation": risk_budgets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
