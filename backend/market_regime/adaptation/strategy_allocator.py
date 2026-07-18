from typing import Dict, Any

class StrategyAllocator:
    """
    Recommends strategy allocation weights based on the current regime and Digital Twin forecasts.
    """
    def __init__(self):
        # Base recommendations by regime
        self.base_weights = {
            "strong_bull": {"Momentum": 40, "Breakout": 30, "SectorRotation": 20, "Volatility": 5, "MeanReversion": 5},
            "weak_bull": {"SectorRotation": 35, "Momentum": 25, "MeanReversion": 20, "Breakout": 10, "Volatility": 10},
            "high_volatility_expansion": {"Volatility": 40, "MeanReversion": 30, "Momentum": 10, "Breakout": 10, "Cash": 10},
            "panic": {"Volatility": 35, "Cash": 40, "MeanReversion": 25, "Momentum": 0, "Breakout": 0},
            "recovery": {"MeanReversion": 40, "Breakout": 30, "SectorRotation": 20, "Momentum": 10, "Volatility": 0},
            "sideways_consolidation": {"MeanReversion": 50, "Volatility": 30, "SectorRotation": 20, "Momentum": 0, "Breakout": 0}
        }
        
    def recommend_allocation(self, current_regime: str, digital_twin_forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates recommended strategy weights.
        """
        base = self.base_weights.get(current_regime, {"Cash": 100}) # default to cash if unknown
        
        # If Digital Twin predicts panic at 20d > 20%, we defensively increase cash
        dist_20d = digital_twin_forecasts.get("20d", {}).get("regime_distribution", {})
        panic_prob = dist_20d.get("panic", 0)
        
        adjusted = base.copy()
        if panic_prob > 0.20:
            adjustment = int(panic_prob * 100 / 2) # e.g. 25% prob -> +12% cash
            if "Cash" not in adjusted:
                adjusted["Cash"] = 0
            
            # Reduce all other strategies proportionally to fund cash
            total_non_cash = sum([v for k, v in adjusted.items() if k != "Cash"])
            for k in adjusted:
                if k != "Cash":
                    adjusted[k] = max(0, adjusted[k] - (adjusted[k] / total_non_cash) * adjustment)
            adjusted["Cash"] += adjustment
            
        # Normalize to 100%
        total = sum(adjusted.values())
        final_weights = {k: round(v * 100 / total, 1) for k, v in adjusted.items()}
        
        return {
            "regime": current_regime,
            "recommended_weights": final_weights,
            "digital_twin_adjustment_applied": panic_prob > 0.20
        }
