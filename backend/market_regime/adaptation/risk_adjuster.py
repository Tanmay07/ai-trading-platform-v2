from typing import Dict, Any

class RiskAdjuster:
    """
    Dynamically adjusts risk budgets and targets based on the market regime.
    """
    def __init__(self):
        self.risk_profiles = {
            "strong_bull": {"target_volatility": 0.18, "max_exposure": 1.5, "stop_loss_multiplier": 1.5, "sector_concentration": 0.30},
            "weak_bull": {"target_volatility": 0.12, "max_exposure": 1.0, "stop_loss_multiplier": 1.2, "sector_concentration": 0.20},
            "high_volatility_expansion": {"target_volatility": 0.10, "max_exposure": 0.8, "stop_loss_multiplier": 0.8, "sector_concentration": 0.15},
            "panic": {"target_volatility": 0.05, "max_exposure": 0.3, "stop_loss_multiplier": 0.5, "sector_concentration": 0.10},
            "recovery": {"target_volatility": 0.15, "max_exposure": 1.2, "stop_loss_multiplier": 1.0, "sector_concentration": 0.25},
            "sideways_consolidation": {"target_volatility": 0.08, "max_exposure": 0.9, "stop_loss_multiplier": 1.0, "sector_concentration": 0.15}
        }
        
    def calculate_risk_budgets(self, current_regime: str, digital_twin_forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns dynamic risk budgets.
        """
        base_risk = self.risk_profiles.get(current_regime, self.risk_profiles["panic"])
        
        # Adjust target volatility down if digital twin expects volatility to spike
        exp_vol_5d = digital_twin_forecasts.get("5d", {}).get("expected_volatility", 15.0)
        
        adjusted_vol = base_risk["target_volatility"]
        if exp_vol_5d > 25.0:
            adjusted_vol *= 0.8 # Reduce target volatility by 20%
            
        budgets = base_risk.copy()
        budgets["target_volatility"] = round(adjusted_vol, 3)
        
        return {
            "regime": current_regime,
            "risk_budgets": budgets,
            "digital_twin_volatility_override": exp_vol_5d > 25.0
        }
