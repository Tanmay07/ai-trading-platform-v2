import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
import pandas as pd

from production_training.deployment.production_registry import ProductionRegistry
from production_training.trainer.production_trainer import ProductionTrainer
from production_training.service.prediction_service import PredictionService
from benchmarking.datasets.dataset_selector import DatasetSelector

router = APIRouter(prefix="/api/production", tags=["Production AI Model"])

def run_training_task():
    trainer = ProductionTrainer()
    # For Phase E4, we train and automatically promote to test the pipeline
    trainer.train_and_register(promote_immediately=True)

@router.post("/retrain")
def trigger_production_training(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_training_task)
    return {"message": "Production Model Training started in the background."}

@router.get("/model")
def get_active_model():
    registry = ProductionRegistry()
    active = registry.get_active_model()
    if not active:
        return {"status": "no_active_model"}
    return active

@router.get("/history")
def get_model_history():
    registry = ProductionRegistry()
    return {
        "active_version": registry.registry.get("active_version"),
        "history": reversed(registry.registry.get("history", []))
    }

@router.post("/rollback")
def rollback_model():
    registry = ProductionRegistry()
    success = registry.rollback()
    if not success:
         raise HTTPException(status_code=400, detail="Rollback failed (possibly at earliest version).")
    return {"message": "Rollback successful.", "new_active_version": registry.registry.get("active_version")}

@router.get("/predict/{symbol}")
def get_prediction(symbol: str):
    """
    Demonstrates the PredictionService abstraction.
    """
    # Load recent features for the symbol from Feature Store (mocked by reading dataset_v3)
    selector = DatasetSelector()
    df = pd.read_parquet(selector.dataset_path)
    sym_df = df[df['symbol'] == symbol]
    if len(sym_df) == 0:
        raise HTTPException(status_code=404, detail="Symbol not found in Feature Store.")
        
    latest_row = sym_df.sort_values('Date').tail(1)
    
    # Send directly to prediction service (we don't need to manually filter columns, it handles it)
    try:
        service = PredictionService()
        prediction = service.predict(latest_row)
        return prediction
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
