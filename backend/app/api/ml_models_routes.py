from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from app.ml.retraining_engine import RetrainingEngine
from app.ml.experiment_tracker import ExperimentTracker
from app.ml.model_registry import ModelRegistry

router = APIRouter(prefix="/api/ml", tags=["ML Pipeline"])

@router.get("/models")
def get_models() -> Dict[str, Any]:
    registry = ModelRegistry()
    active_pack, metadata = registry.load_active_model("champion_ensemble")
    return {
        "active_model": "champion_ensemble",
        "metadata": metadata if metadata else "No active model"
    }

@router.get("/experiments")
def get_experiments() -> List[Dict[str, Any]]:
    tracker = ExperimentTracker()
    return tracker.get_leaderboard()

def run_retraining():
    engine = RetrainingEngine()
    engine.run_pipeline()

@router.post("/retrain")
def trigger_retrain(background_tasks: BackgroundTasks) -> Dict[str, str]:
    background_tasks.add_task(run_retraining)
    return {"status": "accepted", "message": "Retraining job queued in background."}
