from typing import Dict, Any

class TargetEngine:
    def calculate_targets(self, current_price: float, volatility: float, fundamental_status: str) -> Dict[str, float]:
        """
        Calculates Target Price 1, 2, and Stop Loss.
        """
        if current_price <= 0:
            return {"target_1": 0.0, "target_2": 0.0, "stop_loss": 0.0, "cagr": 0.0}
            
        # Volatility impacts the spread. Higher vol -> wider stops and targets.
        spread_multiplier = (volatility / 100.0)
        
        # Base logic
        if fundamental_status == "Undervalued":
            t1 = current_price * (1.0 + (0.15 + spread_multiplier))
            t2 = current_price * (1.0 + (0.25 + spread_multiplier))
            sl = current_price * (1.0 - max(0.05, spread_multiplier * 0.8))
            cagr = 15.0
        elif fundamental_status == "Fairly Valued":
            t1 = current_price * (1.0 + (0.08 + spread_multiplier))
            t2 = current_price * (1.0 + (0.15 + spread_multiplier))
            sl = current_price * (1.0 - max(0.08, spread_multiplier))
            cagr = 8.0
        else: # Overvalued
            t1 = current_price * (1.0 + 0.05)
            t2 = current_price * (1.0 + 0.10)
            sl = current_price * (1.0 - max(0.12, spread_multiplier * 1.5))
            cagr = -5.0
            
        return {
            "target_1": round(t1, 2),
            "target_2": round(t2, 2),
            "stop_loss": round(sl, 2),
            "cagr": round(cagr, 2)
        }
