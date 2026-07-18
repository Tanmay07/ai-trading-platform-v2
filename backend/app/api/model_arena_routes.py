from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import subprocess

router = APIRouter()

class TrainRequest(BaseModel):
    test_size: float = 0.2
    
@router.post("/train_all")
def train_all_models(req: TrainRequest):
    """
    Triggers the Champion Challenger Orchestrator pipeline.
    """
    # For a real system, we'd trigger a Celery task or Airflow DAG here.
    # We will trigger the local script for the prototype.
    script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'run_model_arena.py')
    subprocess.Popen(['python3', script_path])
    
    return {"status": "Training initiated in background"}

@router.get("/champion")
def get_champion():
    """
    Returns the current champion model.
    """
    registry_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_registry.json')
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            reg = json.load(f)
            champ_id = reg.get("champion_id")
            if champ_id:
                return {"champion": reg["models"].get(champ_id)}
    return {"champion": None}

@router.get("/benchmark_report")
def get_benchmark_report():
    """
    Returns the full comparison of all models.
    """
    registry_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_registry.json')
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            reg = json.load(f)
            return {"models": reg.get("models", {}), "champion_id": reg.get("champion_id")}
    return {"models": {}, "champion_id": None}
