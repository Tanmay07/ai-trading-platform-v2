from fastapi import APIRouter, Query, HTTPException
from app.services.technical_orchestrator import TechnicalOrchestrator
from typing import Dict, Any

router = APIRouter(prefix="/api/technical-analysis", tags=["Technical Analysis"])

@router.get("/")
def get_technical_analysis(
    symbol: str = Query(..., description="Stock symbol (e.g., RELIANCE.NS)"),
    sector: str = Query("Unknown", description="Sector name for relative strength")
) -> Dict[str, Any]:
    try:
        orchestrator = TechnicalOrchestrator()
        
        candidate = {
            "Ticker": symbol,
            "Sector": sector
        }
        
        results = orchestrator.analyze_candidates([candidate])
        
        if not results:
            raise HTTPException(status_code=404, detail="Analysis failed or no data found")
            
        result = results[0]
        
        return {
            "symbol": result["Ticker"],
            "breakout_score": result.get("breakout_score", 0),
            "pattern": result.get("Pattern_Name", "None"),
            "relative_strength": result.get("rs_score", 0),
            "sector_rank": result.get("sector_rank", 999),
            "weekly_score": result.get("weekly_score", 0),
            "daily_score": result.get("daily_score", 0),
            "support": result.get("support_level", 0),
            "resistance": result.get("resistance_level", 0),
            "breakout_probability": result.get("breakout_probability", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
