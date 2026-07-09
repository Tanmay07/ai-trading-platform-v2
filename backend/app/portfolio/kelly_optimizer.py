from typing import Dict, Any
from app.config_portfolio import portfolio_config

class KellyOptimizer:
    def calculate_kelly_fraction(self, candidate: Dict[str, Any]) -> float:
        """
        Calculates the Kelly Fraction: f* = p - (q / (b))
        where p = win prob, q = lose prob, b = win/loss ratio.
        """
        # We need expected win prob from ML/RL
        p = float(candidate.get("Confidence", 50)) / 100.0
        q = 1.0 - p
        
        # Assume an average win/loss ratio of 2.0 (e.g., stop loss is half the distance to target)
        # In a real system, we look at the exact ATR stop loss and target distances.
        b = 2.0 
        
        kelly_fraction = p - (q / b)
        
        # Apply safety bounds (e.g., Half-Kelly)
        adjusted_kelly = kelly_fraction * portfolio_config.kelly.fraction_multiplier
        
        # Cap at max config
        final_kelly = min(max(0.0, adjusted_kelly), portfolio_config.kelly.max_kelly_allocation)
        
        return round(final_kelly, 4)
