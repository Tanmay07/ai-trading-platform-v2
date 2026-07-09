from fastapi import APIRouter
from typing import Dict, Any, List
from app.research.research_orchestrator import ResearchOrchestrator
from app.research.strategy_registry import StrategyRegistry
from app.research.factor_library import FactorLibrary

router = APIRouter(prefix="/api/research", tags=["Research Phase 11"])

@router.post("/start")
def start_research_cycle() -> Dict[str, Any]:
    orchestrator = ResearchOrchestrator()
    result = orchestrator.run_discovery_cycle()
    return {"message": "Discovery cycle completed", "candidate": result}

@router.get("/strategies")
def get_candidate_strategies() -> List[Dict[str, Any]]:
    registry = StrategyRegistry()
    return registry.get_candidates()
    
@router.get("/factors")
def get_factors() -> List[Dict[str, Any]]:
    library = FactorLibrary()
    return library.get_top_factors()
