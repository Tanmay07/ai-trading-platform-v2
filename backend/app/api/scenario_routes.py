from fastapi import APIRouter
from scenario_datasets.generator.scenario_registry import ScenarioRegistry

router = APIRouter(prefix="/api/scenarios", tags=["Scenario Datasets"])

@router.get("/")
def get_scenario_dashboard():
    # Provide mock summary statistics for the UI dashboard
    registry = ScenarioRegistry()
    datasets = registry.get_all()
    
    total = len(datasets)
    
    # If DB is empty, provide fake data for visualization
    if total == 0:
        total = 24
        
    return {
        "master_dataset": "ds_classification_v8f9a2b",
        "total_scenarios": total,
        "coverage": 98.4,
        "quality_score": 99.1,
        "distributions": {
            "regime": [
                {"name": "Bull", "value": 45},
                {"name": "Bear", "value": 20},
                {"name": "Sideways", "value": 35}
            ],
            "sector": [
                {"name": "IT", "value": 25},
                {"name": "Banking", "value": 35},
                {"name": "Pharma", "value": 15},
                {"name": "Auto", "value": 25}
            ],
            "volatility": [
                {"name": "High VIX", "value": 20},
                {"name": "Normal", "value": 60},
                {"name": "Low VIX", "value": 20}
            ]
        },
        "top_scenarios": [
            {"name": "Banking Sector", "rows": 850000, "category": "Sector"},
            {"name": "Bull Market", "rows": 2400000, "category": "Regime"},
            {"name": "High Volatility", "rows": 1100000, "category": "Volatility"},
            {"name": "Union Budget", "rows": 125000, "category": "Event"}
        ]
    }

@router.get("/registry")
def get_scenario_registry():
    registry = ScenarioRegistry()
    return registry.get_all()

@router.post("/build")
def trigger_build():
    return {"status": "started", "message": "Scenario Generation triggered."}
