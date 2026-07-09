from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.recommendations.orchestrator import RecommendationEngine

router = APIRouter(prefix="/api/ai-recommendations", tags=["AI Recommendations"])

@router.get("/")
def get_ai_recommendations(portfolio_capital: float = 100000.0, max_positions: int = 5) -> Dict[str, Any]:
    try:
        engine = RecommendationEngine()
        # This will now run Phase 1, 2, 3 and 4 implicitly because of the orchestrator changes.
        results = engine.generate_recommendations(portfolio_capital, max_positions)
        
        # Re-map the payload to fit the Phase 4 requested output
        formatted_recs = []
        for r in results.get("recommendations", []):
            formatted_recs.append({
                "symbol": r.get("Ticker"),
                "recommendation": r.get("Recommendation_Action", "BUY"),
                "confidence": r.get("final_confidence"),
                "consensus": r.get("consensus_score"),
                "technical_score": r.get("TechnicalAgent_Score"),
                "market_score": r.get("MarketAgent_Score"),
                "breakout_score": r.get("BreakoutAgent_Score"),
                "risk_score": r.get("RiskAgent_Score"),
                "portfolio_fit": r.get("PortfolioAgent_Score"),
                "summary": r.get("human_readable_summary"),
                "top_positive_factors": r.get("top_positive_factors", []),
                "top_negative_factors": r.get("top_negative_factors", [])
            })
            
        return {
            "generated_at": results.get("generated_at"),
            "market_status": results.get("market_status"),
            "market_intelligence": results.get("market_intelligence"),
            "recommendations": formatted_recs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
