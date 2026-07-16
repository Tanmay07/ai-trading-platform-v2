import os
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

router = APIRouter(prefix="/api/research", tags=["Alpha Research"])
REPORT_PATH = "data/models/alpha_research_report.json"

def get_report():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Alpha Research Report not found.")
    with open(REPORT_PATH, "r") as f:
        return json.load(f)

@router.get("/overview")
def get_overview():
    return get_report().get("Overview", {})

@router.get("/sectors")
def get_sectors():
    return get_report().get("Sector_Intelligence", {})

@router.get("/features")
def get_features():
    return {
        "Feature_Intelligence": get_report().get("Feature_Intelligence", {}),
        "Feature_Correlation": get_report().get("Feature_Correlation", {})
    }

@router.get("/trades")
def get_trades():
    return get_report().get("Risk_Intelligence", {})

@router.get("/regimes")
def get_regimes():
    return get_report().get("Market_Intelligence", {})

@router.get("/holding-period")
def get_holding_period():
    return get_report().get("Holding_Period_Intelligence", {})

@router.get("/alpha")
def get_alpha():
    return get_report().get("Alpha_Discoveries", [])

@router.get("/recommendations")
def get_recommendations():
    return get_report().get("Recommendation_Center", {})

def run_research_task():
    import subprocess
    subprocess.run(["python3", "alpha_research/reports/research_dashboard.py"], cwd=os.getcwd())

@router.post("/run")
def trigger_research(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_research_task)
    return {"message": "Alpha Research Engine started in the background."}
