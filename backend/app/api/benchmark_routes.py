import os
from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any

from benchmarking.arena.experiment_runner import ExperimentRunner
from benchmarking.arena.promotion_engine import PromotionEngine
from benchmarking.feature_selection.ablation_engine import AblationEngine
from benchmarking.feature_selection.redundancy_detector import RedundancyDetector
from benchmarking.feature_selection.interaction_engine import InteractionEngine
from benchmarking.feature_selection.stability_analyzer import StabilityAnalyzer
from benchmarking.datasets.dataset_selector import DatasetSelector

router = APIRouter(prefix="/api/benchmark", tags=["Champion Challenger Arena"])

# For this demo phase, we store results in memory to serve the UI
_latest_results = {}

def run_full_benchmark():
    global _latest_results
    
    runner = ExperimentRunner()
    results = runner.run_benchmark()
    
    # Run Ablation on hybrid
    hybrid_roc = results.get('hybrid', {}).get('cv_roc_auc', 0.6)
    ablation = AblationEngine().run_ablation(baseline_roc=hybrid_roc)
    
    # Run Feature Selection
    redundancies = RedundancyDetector().detect_redundancies()
    interactions = InteractionEngine().find_interactions(df=None)
    
    selector = DatasetSelector()
    stability = StabilityAnalyzer().analyze_stability(df=None, factors=selector.factors)
    
    # Evaluate Promotion
    champ = results.get('raw', {}) # Pretend raw is our LightGBM v1/v2 baseline
    challenger = results.get('hybrid', {})
    
    engine = PromotionEngine()
    promoted, reason = engine.evaluate_promotion(champ, challenger)
    
    _latest_results = {
        "models": results,
        "champion": "raw", # baseline
        "challengers": ["factors", "hybrid"],
        "promotion_recommendation": {
            "promote": promoted,
            "reason": reason,
            "challenger": "hybrid"
        },
        "feature_intelligence": {
            "ablation": ablation,
            "redundancies": redundancies,
            "interactions": interactions,
            "stability": stability
        }
    }

@router.post("/run")
def trigger_benchmark(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_full_benchmark)
    return {"message": "Institutional Benchmark started in background. Polling recommended."}

@router.get("/report")
def get_benchmark_report():
    if not _latest_results:
        # Mock some results if not run yet to avoid UI crash
        return {"status": "not_run_yet"}
    return _latest_results
