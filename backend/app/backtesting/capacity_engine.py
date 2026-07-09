from typing import Dict, Any

class CapacityEngine:
    def calculate_capacity(self, average_daily_volume: int, current_price: float, max_participation: float) -> float:
        """
        Estimates the maximum deployable capital for a given stock based on liquidity constraints.
        """
        max_trade_volume = average_daily_volume * max_participation
        max_capital = max_trade_volume * current_price
        return max_capital
