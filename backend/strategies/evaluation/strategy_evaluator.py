import random
from typing import Dict, Any

class StrategyEvaluator:
    """
    Simulates walk-forward evaluation of a Strategy Plugin.
    """
    def evaluate(self, strategy_id: str) -> Dict[str, float]:
        random.seed(strategy_id + "_eval")
        
        # Simulate Institutional Metrics
        profit_factor = random.uniform(1.1, 2.8)
        win_rate = random.uniform(0.40, 0.65)
        sharpe = random.uniform(0.8, 3.2)
        max_drawdown = random.uniform(-25.0, -5.0)
        cagr = random.uniform(8.0, 35.0)
        
        return {
            "profit_factor": round(profit_factor, 2),
            "win_rate": round(win_rate, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "cagr_pct": round(cagr, 2)
        }
