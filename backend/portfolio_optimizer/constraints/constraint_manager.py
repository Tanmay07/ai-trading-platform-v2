import yaml
from typing import Dict, Any, List
import logging

logger = logging.getLogger("ConstraintManager")

class ConstraintManager:
    """
    Enforces Hard Constraints (position sizing, sector limits, liquidity).
    """
    def __init__(self):
        with open("config/optimizer.yaml", "r") as f:
            self.config = yaml.safe_load(f)["constraints"]
            
    def filter_universe(self, universe: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters out assets that fail liquidity or regulatory constraints."""
        # MVP: assume all pass
        return universe
        
    def enforce_weight_constraints(self, optimal_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Caps weights based on max_position_weight.
        In reality, this requires iterative re-solving. For MVP, we cap and normalize.
        """
        max_weight = self.config["max_position_weight"] * 100.0
        capped_weights = {}
        excess_weight = 0.0
        
        for sym, weight in optimal_weights.items():
            if weight > max_weight:
                excess_weight += (weight - max_weight)
                capped_weights[sym] = max_weight
            else:
                capped_weights[sym] = weight
                
        # Redistribute excess weight
        n = len(capped_weights)
        if n > 0 and excess_weight > 0:
            distribution = excess_weight / n
            for sym in capped_weights:
                capped_weights[sym] += distribution
                # Re-cap (naive approach for MVP)
                if capped_weights[sym] > max_weight:
                    capped_weights[sym] = max_weight
                    
        return capped_weights
