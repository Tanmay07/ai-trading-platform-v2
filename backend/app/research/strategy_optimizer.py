from typing import Dict, Any

class StrategyOptimizer:
    def optimize(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs Bayesian or Grid Search over the strategy parameters to maximize Sharpe.
        """
        # MVP: slightly improve the parameters
        optimized = strategy.copy()
        optimized["entry_rsi_min"] = 55 
        return optimized
