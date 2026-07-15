from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any, List
import logging

from training_framework.optimization.training_runner import TrainingRunner
from training_framework.registry.experiment_tracker import ExperimentTracker

router = APIRouter(prefix="/api/training", tags=["Training Framework"])
logger = logging.getLogger("TrainingRoutes")

tracker = ExperimentTracker()

@router.get("/experiments")
def get_experiments() -> List[Dict[str, Any]]:
    """Returns all logged training experiments."""
    return tracker.get_experiments()

@router.get("/best")
def get_best_experiment() -> Dict[str, Any]:
    """Returns the experiment with the highest test Win Rate or Profit Factor."""
    experiments = tracker.get_experiments()
    if not experiments:
        return {}
    
    # Sort by test win rate descending (as a proxy for best, adjust as needed)
    valid_exps = [e for e in experiments if e.get("test_metrics")]
    if not valid_exps:
        return experiments[0]
        
    best = max(valid_exps, key=lambda x: x["test_metrics"].get("win_rate", 0))
    return best

def run_background_search():
    try:
        runner = TrainingRunner()
        runner.run_training_cycle()
    except Exception as e:
        logger.error(f"Background Training failed: {e}")

@router.post("/search")
def start_randomized_search(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Kicks off a Randomized Search CV in the background.
    """
    logger.info("Received request to start Randomized Search...")
    background_tasks.add_task(run_background_search)
    return {"message": "Randomized Search initiated in the background. Check logs or /experiments later."}

@router.post("/retrain")
def retrain_model(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Alias for starting the full institutional training cycle.
    """
    return start_randomized_search(background_tasks)

@router.get("/calibration")
def get_calibration_status() -> Dict[str, Any]:
    best = get_best_experiment()
    return {
        "calibration_method": best.get("calibration_method", "N/A"),
        "experiment_id": best.get("experiment_id", "N/A")
    }

@router.get("/threshold")
def get_threshold_status() -> Dict[str, Any]:
    best = get_best_experiment()
    return {
        "optimal_threshold": best.get("optimal_threshold", 50),
        "metrics": best.get("test_metrics", {})
    }
