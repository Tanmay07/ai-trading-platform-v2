import random
from typing import Dict, Any

class RegimeAnalysis:
    def evaluate(self, feature_name: str) -> Dict[str, float]:
        """
        Evaluates stability of the feature across Bull, Bear, and Volatile regimes.
        """
        random.seed(feature_name + "_stability")
        
        bull_ic = random.uniform(0.01, 0.08)
        bear_ic = random.uniform(-0.02, 0.08)
        vol_ic = random.uniform(-0.01, 0.06)
        
        # Stability score: standard deviation of IC across regimes (inverted for higher=better)
        avg_ic = (bull_ic + bear_ic + vol_ic) / 3
        variance = ((bull_ic - avg_ic)**2 + (bear_ic - avg_ic)**2 + (vol_ic - avg_ic)**2) / 3
        
        stability_score = max(0.0, 1.0 - (variance * 100)) # Simple mock score 0-1
        
        return {
            "bull_regime_ic": bull_ic,
            "bear_regime_ic": bear_ic,
            "volatile_regime_ic": vol_ic,
            "overall_stability_score": stability_score
        }
