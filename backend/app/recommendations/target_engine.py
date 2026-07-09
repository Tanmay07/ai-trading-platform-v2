"""
Risk Reward Target Engine
"""
from typing import Dict, Any
from app.config_yaml import trading_config

class TargetEngine:
    def __init__(self):
        self.ratios = trading_config.reward_ratios

    def calculate_targets(self, entry_price: float, stop_loss: float) -> Dict[str, Any]:
        """
        Calculates profit targets based on predefined reward multiples of the risk amount.
        """
        risk = entry_price - stop_loss
        if risk <= 0:
            return {}
            
        target_1 = entry_price + (risk * self.ratios.target_1)
        target_2 = entry_price + (risk * self.ratios.target_2)
        target_3 = entry_price + (risk * self.ratios.target_3)
        
        expected_return_pct = ((target_1 - entry_price) / entry_price) * 100
        
        return {
            "target_1": round(target_1, 2),
            "target_2": round(target_2, 2),
            "target_3": round(target_3, 2),
            "expected_return_percent": round(expected_return_pct, 2),
            "reward_risk_ratio": round(self.ratios.target_1, 2),
            "potential_profit_per_share": round(target_1 - entry_price, 2),
            "potential_loss_per_share": round(risk, 2)
        }
