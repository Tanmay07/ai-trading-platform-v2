from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
import os
import pandas as pd
from feature_platform.engine.feature_pipeline import FeaturePipeline
from feature_platform.storage.feature_store import FeatureStore
from feature_platform.validation.feature_validator import FeatureValidator
from data_platform.universe.universe_manager import UniverseManager
from data_platform.universe.universe_db import UniverseDB
from pydantic import BaseModel

logger = logging.getLogger("FeatureRoutes")
router = APIRouter()

pipeline = FeaturePipeline()
store = FeatureStore()
validator = FeatureValidator()
universe = UniverseManager(db_manager=UniverseDB())

class GenerateRequest(BaseModel):
    symbol: str

@router.get("/status")
async def get_feature_status():
    """Returns the total number of features generated and coverage."""
    active_symbols = [u.symbol for u in universe.fetch_active_universe()]
    total_active = len(active_symbols)
    
    generated_count = 0
    total_features = 0
    last_version = "v1.0"
    
    for symbol in active_symbols:
        path = store._get_path(symbol)
        if os.path.exists(path):
            generated_count += 1
            if total_features == 0:
                # Count features from the first found parquet
                try:
                    df = pd.read_parquet(path)
                    total_features = len(df.columns) - 5 # subtract OHLCV
                except:
                    pass
                    
    coverage = round((generated_count / total_active) * 100, 2) if total_active > 0 else 0
    
    return {
        "status": "active",
        "total_features": total_features,
        "latest_version": last_version,
        "coverage_percent": coverage,
        "generated_symbols": generated_count,
        "total_universe": total_active
    }

@router.get("/quality")
async def get_feature_quality():
    """Returns overall feature quality metrics across a sample."""
    active_symbols = [u.symbol for u in universe.fetch_active_universe()]
    sample = active_symbols[:10] # take a sample for speed
    
    total_score = 0
    valid_count = 0
    total_checked = 0
    
    for symbol in sample:
        path = store._get_path(symbol)
        if os.path.exists(path):
            df = pd.read_parquet(path)
            res = validator.validate(df)
            total_score += res['score']
            if res['valid']: valid_count += 1
            total_checked += 1
            
    avg_score = round(total_score / total_checked, 2) if total_checked > 0 else 0
    
    return {
        "overall_quality_score": avg_score,
        "sample_size": total_checked,
        "valid_datasets": valid_count
    }

@router.post("/generate")
async def generate_features(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Triggers generation for a single symbol in the background."""
    background_tasks.add_task(pipeline.run_pipeline, req.symbol)
    return {"message": f"Feature generation started for {req.symbol}"}
    
@router.post("/recalculate")
async def recalculate_all(background_tasks: BackgroundTasks):
    """Triggers generation for ALL symbols."""
    active_symbols = [u.symbol for u in universe.fetch_active_universe()]
    for symbol in active_symbols:
         background_tasks.add_task(pipeline.run_pipeline, symbol)
    return {"message": f"Recalculation started for {len(active_symbols)} symbols"}
