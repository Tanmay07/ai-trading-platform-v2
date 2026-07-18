import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("TargetEngine")

class TargetEngine:
    def __init__(self, min_risk_reward: float = 2.0):
        self.min_risk_reward = min_risk_reward
        
    def generate_targets(self, entry_price: float, stop_loss: float) -> Tuple[float, float, float, float]:
        """
        Returns (Target 1, Target 2, Stretch Target, Risk/Reward Ratio)
        """
        risk = entry_price - stop_loss
        if risk <= 0:
             return 0.0, 0.0, 0.0, 0.0
             
        # Generate baseline targets using R-multiples
        target_1 = entry_price + (risk * self.min_risk_reward)
        target_2 = entry_price + (risk * (self.min_risk_reward + 1.0))
        stretch = entry_price + (risk * (self.min_risk_reward + 2.5))
        
        # In a real system, we might adjust these based on resistance levels
        # Here we rely on the strict mathematical R-multiples
        
        rr_ratio = (target_2 - entry_price) / risk
        
        return round(target_1, 2), round(target_2, 2), round(stretch, 2), round(rr_ratio, 2)
