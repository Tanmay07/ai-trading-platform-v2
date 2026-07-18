import logging
from typing import Dict, Any, List

logger = logging.getLogger("AllocationEngine")

class AllocationEngine:
    """
    Allocates capital across strategies based on performance and risk weighting.
    """
    def compute_allocation(self, strategy_evaluations: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Takes a dict of {strategy_id: metrics}.
        Returns a dict of {strategy_id: allocation_percentage}.
        """
        allocations = {}
        total_weight = 0.0
        
        # Simple Risk-Adjusted Performance Weighting (Sharpe * Profit Factor)
        weights = {}
        for s_id, metrics in strategy_evaluations.items():
            if metrics["sharpe_ratio"] > 0 and metrics["profit_factor"] > 1.0:
                # Penalty for high drawdown
                dd_penalty = 1.0 - (abs(metrics["max_drawdown_pct"]) / 100.0)
                weight = metrics["sharpe_ratio"] * metrics["profit_factor"] * dd_penalty
            else:
                weight = 0.0 # Don't allocate if unprofitable or negative sharpe
                
            weights[s_id] = weight
            total_weight += weight
            
        # Normalize to 100%
        if total_weight > 0:
            for s_id, w in weights.items():
                allocations[s_id] = round((w / total_weight) * 100, 2)
        else:
            # Equal weight fallback
            count = len(strategy_evaluations)
            for s_id in strategy_evaluations:
                allocations[s_id] = round(100.0 / count, 2)
                
        return allocations
