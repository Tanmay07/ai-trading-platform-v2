from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel
from model_training.registry.model_registry import ModelRegistry
from typing import List

logger = logging.getLogger("ModelRoutes")
router = APIRouter()
registry = ModelRegistry()

class PredictionRequest(BaseModel):
    features: dict

@router.get("/current")
async def get_current_model_metadata():
    """Returns metadata for the active production model."""
    _, _, _, metadata = registry.get_production_model()
    if not metadata:
        raise HTTPException(status_code=404, detail="No production model found.")
    return metadata

@router.get("/history")
async def get_model_history():
    """Returns the history of all registered models."""
    return registry.registry["models"]
