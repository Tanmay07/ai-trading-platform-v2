import logging
import pandas as pd
from typing import List, Dict

logger = logging.getLogger("PortfolioOptimizer")

class PortfolioOptimizer:
    """
    Position Sizing & Portfolio Construction Engine.
    """
    def __init__(self, max_weight_per_asset: float = 0.2, max_sector_weight: float = 0.4):
        self.max_weight_per_asset = max_weight_per_asset
        self.max_sector_weight = max_sector_weight
        
    def calculate_position_size(self, recommendation: Dict, cash_balance: float, portfolio_value: float) -> Dict:
        """
        Determines the optimal investment amount for a new recommendation.
        Returns suggested capital allocation and risk budget.
        """
        if cash_balance <= 0:
            return {"suggested_investment": 0.0, "reason": "Insufficient cash"}
            
        conf = recommendation.get('confidence', 0.5)
        
        # Base weight based on conviction (Kelly Criterion inspired heuristic)
        # Assuming probability of win = conf, win/loss ratio = 1.0
        # Kelly % = W - ((1 - W) / R)
        kelly_fraction = max(0.0, conf - ((1.0 - conf) / 1.0)) 
        
        # Dampen the kelly fraction for institutional safety (half-kelly)
        target_weight = kelly_fraction * 0.5
        
        # Constrain to max weight limit
        target_weight = min(target_weight, self.max_weight_per_asset)
        
        target_capital = portfolio_value * target_weight
        
        # Constrain to available cash
        investment = min(target_capital, cash_balance)
        
        return {
            "suggested_investment": float(investment),
            "target_weight": float(investment / portfolio_value) if portfolio_value > 0 else 0.0,
            "max_allocation": float(portfolio_value * self.max_weight_per_asset),
            "risk_budget_consumption": float(target_weight * 1.5) # heuristic
        }
