import logging
from typing import Dict, Any, List

from strategies.registry.strategy_registry import StrategyRegistry
from strategies.evaluation.strategy_evaluator import StrategyEvaluator
from strategies.evaluation.correlation_analyzer import CorrelationAnalyzer
from strategies.allocation.allocation_engine import AllocationEngine

# Import strategy plugins
from strategies.plugins.momentum import MomentumStrategy
from strategies.plugins.mean_reversion import MeanReversionStrategy
from strategies.plugins.breakout import BreakoutStrategy
from strategies.plugins.sector_rotation import SectorRotationStrategy
from strategies.plugins.volatility import VolatilityStrategy

logger = logging.getLogger("StrategyPortfolio")

class StrategyPortfolio:
    """
    The Strategy Portfolio Layer (Middle Layer of the Hierarchical Architecture).
    Combines signals from all strategies, resolves conflicts, applies capital allocation,
    and produces a unified opportunity set.
    """
    def __init__(self):
        self.registry = StrategyRegistry()
        self.evaluator = StrategyEvaluator()
        self.correlation = CorrelationAnalyzer()
        self.allocator = AllocationEngine()
        
        # Load plugins
        self.plugins = {
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy(),
            "sector_rotation": SectorRotationStrategy(),
            "volatility": VolatilityStrategy()
        }
        
    def rebuild_portfolio(self):
        """
        Runs the full evaluation and allocation cycle.
        """
        logger.info("Rebuilding Strategy Portfolio")
        
        # 1. Evaluate all plugins and register them
        evaluations = {}
        for s_id, plugin in self.plugins.items():
            self.registry.register_strategy(s_id, plugin.get_metadata())
            metrics = self.evaluator.evaluate(s_id)
            self.registry.update_evaluation(s_id, metrics)
            
            # Simple governance: promote if Sharpe > 1.25 and Profit Factor > 1.4
            if metrics["sharpe_ratio"] > 1.25 and metrics["profit_factor"] > 1.4:
                self.registry.promote_strategy(s_id, "Production")
            else:
                self.registry.promote_strategy(s_id, "Candidate")
                
            evaluations[s_id] = metrics
            
        # 2. Compute Allocation
        allocations = self.allocator.compute_allocation(evaluations)
        logger.info(f"New Capital Allocation: {allocations}")
        
        return allocations
