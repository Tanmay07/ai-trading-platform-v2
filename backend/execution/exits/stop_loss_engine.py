import logging
from typing import Dict, Any

logger = logging.getLogger("StopLossEngine")

class StopLossEngine:
    def __init__(self, multiplier: float = 2.0):
        self.multiplier = multiplier
        
    def generate_stop_loss(self, entry_price: float, position: Dict[str, Any]) -> float:
        """
        Generates an adaptive stop loss based on ATR.
        """
        atr = position.get("atr", entry_price * 0.02) # Fallback to 2% if ATR missing
        
        # Long only for now
        stop_price = entry_price - (atr * self.multiplier)
        
        # Ensure stop isn't negative or invalid
        if stop_price <= 0:
             logger.warning(f"Calculated negative stop loss {stop_price} for {position.get('symbol')}. Clamping to 50% max drawdown.")
             stop_price = entry_price * 0.5
             
        return round(stop_price, 2)
