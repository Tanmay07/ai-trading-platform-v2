import os
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()
REPORT_PATH = "data/models/validation_report.json"

@router.get("/report", response_model=Dict[str, Any])
def get_validation_report():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Validation report not found. Run validation script.")
        
    with open(REPORT_PATH, "r") as f:
        return json.load(f)

@router.get("/leakage", response_model=Dict[str, Any])
def get_leakage_audit():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Validation report not found.")
        
    with open(REPORT_PATH, "r") as f:
        data = json.load(f)
        return data.get("Leakage_Audit", {})

@router.get("/correlation", response_model=Dict[str, Any])
def get_correlation_audit():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Validation report not found.")
        
    with open(REPORT_PATH, "r") as f:
        data = json.load(f)
        return data.get("Ranking_Correlation_Audit", {})
