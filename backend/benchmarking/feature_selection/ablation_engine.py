import logging
import pandas as pd
from typing import List, Dict, Any
from benchmarking.datasets.dataset_selector import DatasetSelector
from training_framework.optimization.training_runner import TrainingRunner

logger = logging.getLogger("AblationEngine")

class AblationEngine:
    def __init__(self):
        self.selector = DatasetSelector()
        
    def run_ablation(self, baseline_roc: float) -> List[Dict[str, Any]]:
        """
        Iteratively drops one factor from the Hybrid dataset, retrains the model,
        and measures the performance drop.
        """
        logger.info("Starting Feature Ablation (Drop-One) Analysis...")
        
        # We start with the full Hybrid dataset
        hybrid_df = self.selector.load_mode("hybrid")
        factors = self.selector.factors
        
        results = []
        for factor in factors:
            if factor not in hybrid_df.columns:
                continue
                
            logger.info(f"Ablating factor: {factor}")
            ablated_df = hybrid_df.drop(columns=[factor])
            
            # Re-instantiate runner for clean state
            runner = TrainingRunner()
            exp_data = runner.run_training_cycle(df=ablated_df)
            
            ablated_roc = exp_data.get("cv_score_roc_auc", 0)
            roc_drop = baseline_roc - ablated_roc
            
            if roc_drop > 0.01:
                classification = "Essential"
            elif roc_drop > 0.001:
                classification = "Helpful"
            elif roc_drop < -0.005:
                classification = "Harmful"
            else:
                classification = "Neutral"
                
            results.append({
                "factor": factor,
                "ablated_roc": ablated_roc,
                "performance_impact": -roc_drop, # negative means it dropped (factor was good)
                "classification": classification
            })
            
        # Sort by most essential (largest drop when removed)
        results = sorted(results, key=lambda x: x["performance_impact"])
        return results
