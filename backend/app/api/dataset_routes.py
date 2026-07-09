from fastapi import APIRouter
from dataset_platform.storage.dataset_registry import DatasetRegistry

router = APIRouter(prefix="/api/datasets", tags=["Dataset Engineering"])

@router.get("/")
def get_dataset_dashboard():
    # Mock data for frontend
    registry = DatasetRegistry()
    datasets = registry.get_all()
    
    latest_version = "v1.0"
    total_rows = 5400000
    if datasets:
        latest = datasets[0]
        latest_version = latest.version_id
        total_rows = latest.total_rows
        
    return {
        "latest_version": latest_version,
        "total_rows": total_rows,
        "features": 228,
        "quality_score": 99.2,
        "leakage": 0,
        "generated": "Today 16:45",
        "label_distribution": [
            {"name": "Strong Buy", "value": 15},
            {"name": "Buy", "value": 25},
            {"name": "Hold", "value": 40},
            {"name": "Sell", "value": 15},
            {"name": "Strong Sell", "value": 5}
        ],
        "growth": [
            {"year": "2020", "rows": 1.2},
            {"year": "2021", "rows": 2.1},
            {"year": "2022", "rows": 3.4},
            {"year": "2023", "rows": 4.5},
            {"year": "2024", "rows": 5.4}
        ]
    }

@router.get("/registry")
def get_dataset_registry():
    registry = DatasetRegistry()
    return registry.get_all()

@router.post("/build")
def trigger_build():
    return {"status": "started", "message": "Dataset generation pipeline triggered."}
