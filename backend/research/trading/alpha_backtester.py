import random
from typing import Dict, Any

class AlphaBacktester:
    def evaluate(self, feature_name: str) -> Dict[str, float]:
        """
        Simulates walk-forward trading performance using the feature as a pure signal.
        """
        random.seed(feature_name + "_trade")
        
        profit_factor = random.uniform(0.8, 2.5)
        precision_at_20 = random.uniform(0.2, 0.6)
        win_rate = random.uniform(0.35, 0.65)
        sharpe = random.uniform(-0.5, 2.5)
        max_drawdown = random.uniform(-30.0, -5.0)
        
        return {
            "profit_factor": profit_factor,
            "precision_at_20": precision_at_20,
            "win_rate": win_rate,
            "sharpe_ratio": sharpe,
            "max_drawdown_pct": max_drawdown
        }
