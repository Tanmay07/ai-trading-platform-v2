from fastapi import APIRouter
from feature_platform.storage.feature_registry import FeatureRegistry
from feature_platform.validation.feature_quality import FeatureQualityValidator

router = APIRouter(prefix="/api/features", tags=["Feature Intelligence"])

@router.get("/")
def get_features_dashboard():
    # Mock data for frontend
    registry = FeatureRegistry().get_catalog()
    return {
        "total_features": len(registry) + 140, # Mocking the ~200 number
        "latest_version": "v1.0",
        "quality_score": 98,
        "last_updated": "Today 15:30",
        "categories": [
            {"name": "Trend", "count": 25},
            {"name": "Momentum", "count": 18},
            {"name": "Volatility", "count": 14},
            {"name": "Volume", "count": 12},
            {"name": "Breakout", "count": 10},
        ],
        "top_features": list(registry.keys())[:5]
    }

@router.get("/registry")
def get_feature_registry():
    return FeatureRegistry().get_catalog()

@router.post("/generate")
def trigger_generation():
    return {"status": "started", "message": "Incremental feature generation pipeline triggered."}
