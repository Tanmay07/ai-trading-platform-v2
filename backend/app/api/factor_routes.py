import os
import yaml
import pandas as pd
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from factor_engine.validation.factor_validator import FactorValidator

router = APIRouter(prefix="/api/factors", tags=["Factor Intelligence"])

V3_PATH = "data/ml_datasets/dataset_v3.parquet"
factors_list = [
    "Trend_Factor", "Relative_Strength_Factor", "Breakout_Quality_Factor",
    "Volatility_Factor", "Liquidity_Factor", "Market_Breadth_Factor",
    "Regime_Factor", "Risk_Factor", "Momentum_Factor", "Institutional_Activity_Factor"
]

@router.get("/")
def get_factors_overview():
    if not os.path.exists(V3_PATH):
        raise HTTPException(status_code=404, detail="Feature Store V2 not found (dataset_v3.parquet)")
    
    df = pd.read_parquet(V3_PATH)
    val = FactorValidator.validate_factors(df)
    return val

@router.get("/{symbol}")
def get_factor_for_symbol(symbol: str):
    if not os.path.exists(V3_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    df = pd.read_parquet(V3_PATH)
    sym_df = df[df['symbol'] == symbol]
    if len(sym_df) == 0:
        raise HTTPException(status_code=404, detail="Symbol not found")
        
    # Get latest row for the symbol
    latest = sym_df.sort_values('Date').iloc[-1]
    
    res = {}
    for f in factors_list:
        res[f] = round(float(latest.get(f, 0.0)), 2)
        
    return res

def run_factor_engine_task():
    import subprocess
    subprocess.run(["python3", "factor_engine/builder/feature_store_v2.py"], cwd=os.getcwd())

@router.post("/recalculate")
def trigger_recalculate(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_factor_engine_task)
    return {"message": "Feature Store V2 recalculation started in the background."}
