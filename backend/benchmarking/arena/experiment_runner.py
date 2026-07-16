import logging
from typing import Dict, Any
from benchmarking.datasets.dataset_selector import DatasetSelector
from training_framework.optimization.training_runner import TrainingRunner

logger = logging.getLogger("ExperimentRunner")

class ExperimentRunner:
    def __init__(self):
        self.selector = DatasetSelector()
        
    def run_benchmark(self) -> Dict[str, Any]:
        """
        Runs the full Phase E3.7 benchmark: Raw vs Factors vs Hybrid.
        Returns the benchmark results.
        """
        modes = self.selector.config.get("feature_modes", ["raw", "factors", "hybrid"])
        
        results = {}
        for mode in modes:
            logger.info(f"--- Starting Benchmark for Feature Mode: {mode.upper()} ---")
            df = self.selector.load_mode(mode)
            
            # Re-instantiate TrainingRunner to ensure clean state
            runner = TrainingRunner()
            
            # The runner will handle randomized search, calibration, and threshold opt
            exp_data = runner.run_training_cycle(df=df)
            
            # Extract key metrics for comparison
            metrics = exp_data.get("test_metrics", {})
            results[mode] = {
                "experiment_id": exp_data.get("id"),
                "cv_roc_auc": exp_data.get("cv_score_roc_auc"),
                "test_precision_20": metrics.get("Precision@20", 0.0),
                "test_profit_factor": metrics.get("Profit_Factor", 0.0),
                "test_win_rate": metrics.get("Win_Rate", 0.0),
                "training_time_seconds": exp_data.get("training_time_seconds")
            }
            logger.info(f"--- Completed Benchmark for {mode.upper()} ---")
            
        return results
