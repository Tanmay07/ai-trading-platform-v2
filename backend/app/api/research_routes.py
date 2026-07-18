from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from research.registry.alpha_registry import AlphaRegistry
from research.alpha_lab.signal_discovery import SignalDiscoveryEngine

router = APIRouter(tags=["research"])
registry = AlphaRegistry()

@router.get("/features")
def get_alpha_marketplace():
    """
    Retrieves all signals currently in the Alpha Marketplace.
    """
    try:
        signals = registry.list_all_signals()
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-experiment")
def run_alpha_discovery_experiment():
    """
    Triggers the generation and evaluation of candidate features through the R&D pipeline.
    """
    try:
        engine = SignalDiscoveryEngine()
        engine.run_discovery_pipeline()
        return {"message": "Alpha Discovery Pipeline completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
