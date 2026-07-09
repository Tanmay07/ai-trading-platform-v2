"""
Dynamic Risk Engine
Responsible for portfolio risk calculations.
"""
from typing import Dict
from app.config_yaml import trading_config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RiskEngine:
    def __init__(self):
        self.config = trading_config.risk_management

    def calculate_risk_limits(
        self,
        portfolio_capital: float,
        current_exposure: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculates maximum capital allocation and monetary risk per trade.
        """
        max_alloc = portfolio_capital * (self.config.max_position_allocation_percent / 100.0)
        max_risk = portfolio_capital * (self.config.max_portfolio_risk_percent / 100.0)
        
        buying_power = max(0, portfolio_capital - current_exposure)
        
        return {
            "max_capital_allocation": max_alloc,
            "max_monetary_risk": max_risk,
            "available_buying_power": buying_power,
            "remaining_portfolio_risk": max_risk
        }
