from fastapi import APIRouter
from typing import Dict, Any

from decision_engine.orchestrator.meta_decision_engine import MetaDecisionEngine
from decision_engine.ranking.probability_calibrator import ProbabilityCalibrator
from decision_engine.ranking.opportunity_ranker import OpportunityRanker
from data_platform.core.config_manager import ConfigManager

router = APIRouter(prefix="/api/decision", tags=["Meta Decision Engine"])

# Initialize singletons (In production, use dependency injection)
config_manager = ConfigManager()
decision_engine = MetaDecisionEngine(config_manager)

@router.get("/explain/{symbol}")
async def explain_decision(symbol: str) -> Dict[str, Any]:
    """
    Evaluates a specific symbol and returns an explainable decision.
    In a real app, `raw_inputs` would be fetched from D2 Feature Store and D3 Redis Cache.
    Here we use mock inputs to demonstrate the engine.
    """
    # Mock inputs
    raw_inputs = {
        "vix": 12.5, # Low VIX = Bull/Neutral
        "nifty_trend": "UP",
        "rsi": 65,
        "price": 105,
        "sma20": 100,
        "relative_volume": 1.5,
        "sentiment_importance": 90, # High positive news impact
        "portfolio_exposure": 0.0,
        "ml_probability": 0.75,
        "model_agreement": 0.9,
        "data_freshness": 1.0
    }
    
    # Run probability calibration on the raw ML input
    calibrated_prob = ProbabilityCalibrator.calibrate(raw_inputs["ml_probability"])
    raw_inputs["ml_probability"] = calibrated_prob
    
    decision = decision_engine.evaluate(symbol, raw_inputs)
    return decision

@router.get("/top")
async def get_top_decisions(limit: int = 10) -> Dict[str, Any]:
    """
    Mocks running the decision engine over a batch of stocks and ranks them.
    """
    stocks = ["BEL", "RELIANCE", "TCS", "INFY", "HDFCBANK"]
    decisions = []
    
    # We will just vary the ML probability mock to get different scores
    for i, symbol in enumerate(stocks):
        raw_inputs = {
            "vix": 12.5,
            "nifty_trend": "UP",
            "rsi": 65,
            "price": 105,
            "sma20": 100,
            "relative_volume": 1.5,
            "sentiment_importance": 80 - (i * 10),
            "portfolio_exposure": 0.0,
            "ml_probability": 0.9 - (i * 0.1),
            "model_agreement": 0.9,
            "data_freshness": 1.0
        }
        decisions.append(decision_engine.evaluate(symbol, raw_inputs))
        
    ranked = OpportunityRanker.rank(decisions, top_n=limit)
    return {"top_opportunities": ranked}
