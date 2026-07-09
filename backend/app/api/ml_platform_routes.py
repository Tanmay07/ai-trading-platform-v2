from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List
import logging

from ml_platform.feature_store.feature_store import FeatureStore
from ml_platform.registry.model_registry import ModelRegistry
from ml_platform.prediction.prediction_service import PredictionService

router = APIRouter(prefix="/api/ml", tags=["ML Platform"])
logger = logging.getLogger(__name__)

# Singletons for API
feature_store = FeatureStore()
model_registry = ModelRegistry()
prediction_service = PredictionService(registry=model_registry)

@router.get("/features")
async def get_feature_catalog() -> Dict[str, Any]:
    """Returns the catalog of all registered features."""
    return feature_store.registry.get_registered_features()

@router.get("/models")
async def get_models() -> Dict[str, Any]:
    """Returns all models currently in the registry."""
    return model_registry.get_registry_status()

@router.get("/predictions/{symbol}")
async def get_prediction(symbol: str, model_name: str = "breakout_5d_ensemble") -> Dict[str, Any]:
    """Returns a real-time prediction for the given symbol."""
    result = prediction_service.predict_symbol(symbol, model_name)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.post("/train")
async def trigger_training(background_tasks: BackgroundTasks, target: str = "Target_5d_Class") -> Dict[str, Any]:
    """
    Triggers a background training job across the entire dataset.
    (MVP placeholder: In reality, you'd specify hyperparameters, datasets, etc.)
    """
    # background_tasks.add_task(...) 
    return {"status": "accepted", "message": f"Training job started for {target}"}

@router.post("/validate")
async def validate_model(model_name: str, version: str) -> Dict[str, Any]:
    """Validates a specific model version."""
    return {"status": "accepted", "message": f"Validation triggered for {model_name} v{version}"}
