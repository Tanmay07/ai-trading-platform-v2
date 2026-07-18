from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from adaptive_learning.engine.adaptive_engine import AdaptiveEngine

router = APIRouter(tags=["adaptive"])

@router.get("/health")
def get_system_health():
    """
    Runs the adaptive intelligence engine and returns system health, drift analysis, 
    recommendations, and the AI-CIO executive briefing.
    """
    try:
        engine = AdaptiveEngine()
        result = engine.analyze_system_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
