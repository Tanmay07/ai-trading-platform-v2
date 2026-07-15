import numpy as np
import pandas as pd
from typing import Dict, Any, List
import logging
from .trading_metrics import calculate_advanced_trading_metrics

logger = logging.getLogger("ThresholdOptimizer")

class ThresholdOptimizer:
    def __init__(self, config_path: str = "config/training_framework.yaml"):
        # Default range from config
        self.thresholds = [50, 55, 60, 65, 70, 75, 80, 85]
        
    def optimize_threshold(self, y_prob: np.ndarray, y_true: pd.Series, trade_returns: pd.Series) -> Dict[str, Any]:
        """
        Sweeps through thresholds, calculates trading metrics, and picks the one 
        that maximizes Profit Factor and Win Rate.
        """
        logger.info(f"Optimizing thresholds: {self.thresholds}")
        results = []
        
        # Ensure y_prob is 1D
        if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
            y_prob = y_prob[:, 1]
            
        for t in self.thresholds:
            t_prob = t / 100.0
            y_pred_binary = (y_prob >= t_prob).astype(int)
            
            y_pred_series = pd.Series(y_pred_binary, index=y_true.index)
            
            metrics = calculate_advanced_trading_metrics(y_true, y_pred_series, trade_returns)
            if not metrics:
                continue
                
            metrics["threshold"] = t
            results.append(metrics)
            
        if not results:
            return {"optimal_threshold": 50, "metrics": {}}
            
        # Select optimal based on Profit Factor > 1.5 and highest Win Rate
        valid = [r for r in results if r["profit_factor"] >= 1.2 and r["total_trades"] > 50]
        if not valid:
            # Fallback to max profit factor
            best = max(results, key=lambda x: x["profit_factor"])
        else:
            best = max(valid, key=lambda x: x["win_rate"])
            
        logger.info(f"Optimal Threshold Selected: {best['threshold']}%")
        return {
            "optimal_threshold": best["threshold"],
            "metrics": best,
            "all_results": results
        }
