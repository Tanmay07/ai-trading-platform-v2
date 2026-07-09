"""
Recommendation API Routes
"""
from fastapi import APIRouter, Query, HTTPException
from app.recommendations.orchestrator import RecommendationEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/")
def get_recommendations(
    capital: float = Query(..., description="Total portfolio capital available"),
    risk_percent: float = Query(None, description="Override max risk percent"),
    max_positions: int = Query(None, description="Max number of recommendations to return"),
    sector: str = Query(None, description="Filter by sector"),
    market_cap: float = Query(None, description="Minimum market cap override"),
    confidence: float = Query(None, description="Minimum confidence score override")
):
    try:
        engine = RecommendationEngine()
        if risk_percent is not None:
            # Temporarily override config for this request
            engine.risk_engine.config.max_portfolio_risk_percent = risk_percent
            
        result = engine.generate_recommendations(
            portfolio_capital=capital,
            max_positions=max_positions,
            sector=sector,
            market_cap=market_cap,
            confidence=confidence
        )
        return result
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
