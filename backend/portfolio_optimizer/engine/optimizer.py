import logging
import yaml
from typing import Dict, Any, List

from portfolio_optimizer.models.optimization_solvers import OptimizationSolvers
from portfolio_optimizer.constraints.constraint_manager import ConstraintManager
from portfolio_optimizer.risk.risk_engine import RiskEngine

logger = logging.getLogger("PortfolioOptimizer")

class PortfolioOptimizerEngine:
    """
    The central optimizer engine that orchestrates the opportunity set through
    risk estimation, constraints, and mathematical solvers.
    """
    def __init__(self):
        with open("config/optimizer.yaml", "r") as f:
            self.config = yaml.safe_load(f)["optimizer"]
            
        self.solvers = OptimizationSolvers()
        self.constraint_manager = ConstraintManager()
        self.risk_engine = RiskEngine()
        
    def optimize(self, opportunity_universe: List[Dict[str, Any]], method: str = None) -> Dict[str, Any]:
        """
        Runs the full optimization pipeline.
        """
        opt_method = method or self.config["default_model"]
        logger.info(f"Starting Portfolio Optimization using {opt_method}")
        
        # 1. Evaluate Constraints on Universe (e.g. liquidity limits)
        filtered_universe = self.constraint_manager.filter_universe(opportunity_universe)
        
        # 2. Risk Estimation (Volatility, Covariance)
        risk_metrics = self.risk_engine.estimate_risk(filtered_universe)
        
        # 3. Solve for optimal weights
        optimal_weights = self.solvers.solve(opt_method, filtered_universe)
        
        # 4. Enforce Hard Constraints on Weights
        final_weights = self.constraint_manager.enforce_weight_constraints(optimal_weights)
        
        return {
            "method": opt_method,
            "weights": final_weights,
            "risk_metrics": risk_metrics,
            "status": "OPTIMAL"
        }
