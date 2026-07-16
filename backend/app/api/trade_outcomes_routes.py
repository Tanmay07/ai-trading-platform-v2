from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pandas as pd
import os
import yaml
from trade_outcomes.registry.label_registry import LabelRegistry

router = APIRouter()
registry = LabelRegistry()

DATASET_PATH = "data/ml_datasets/dataset_v1.parquet"

@router.get("/labels", response_model=Dict[str, Any])
def get_label_versions():
    """Returns all label versions from the registry"""
    return {"versions": registry.get_all_versions()}

@router.get("/labels/comparison", response_model=Dict[str, Any])
def get_label_comparison():
    """Returns the latest label comparison metrics"""
    latest = registry.get_latest_version()
    if not latest:
        raise HTTPException(status_code=404, detail="No label comparisons found.")
    return latest

@router.get("/mfe-mae-dist", response_model=Dict[str, Any])
def get_mfe_mae_distribution():
    """Returns a downsampled distribution of MFE and MAE for plotting"""
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    df = pd.read_parquet(DATASET_PATH)
    
    if 'MFE_Pct' not in df.columns or 'MAE_Pct' not in df.columns:
        raise HTTPException(status_code=400, detail="Trade replay has not been executed yet")
        
    # Downsample for UI performance
    sample_df = df[['MFE_Pct', 'MAE_Pct']].sample(min(10000, len(df)), random_state=42)
    
    return {
        "mfe": sample_df['MFE_Pct'].tolist(),
        "mae": sample_df['MAE_Pct'].tolist()
    }

@router.get("/quality-distribution", response_model=Dict[str, Any])
def get_trade_quality_distribution():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    df = pd.read_parquet(DATASET_PATH)
    
    if 'Trade_Quality_Category' not in df.columns:
        raise HTTPException(status_code=400, detail="Trade Quality Score not found. Run trade replay.")
        
    dist = df['Trade_Quality_Category'].value_counts().to_dict()
    avg_score = df['Trade_Quality_Score'].mean()
    
    return {
        "distribution": dist,
        "average_score": round(avg_score, 2)
    }
