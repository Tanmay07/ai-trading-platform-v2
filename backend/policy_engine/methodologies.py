from typing import Dict, Any

class MethodologyEngine:
    """
    Executes dynamic logic for Targets and Stop Losses based on the JSON configuration
    stored in the Policy Version.
    """
    
    @staticmethod
    def calculate_targets(current_price: float, volatility: float, target_logic: Dict[str, Any]) -> Dict[str, float]:
        """
        Executes the methodology specified in target_logic.
        """
        method = target_logic.get("methodology", "RISK_REWARD")
        params = target_logic.get("params", {})
        
        if current_price <= 0:
            return {"target_1": 0.0, "target_2": 0.0, "cagr": 0.0}
            
        if method == "ATR_PROJECTION":
            # In a real system, ATR is fetched. Here we mock it via volatility
            mock_atr = current_price * (volatility / 100.0) * 0.1
            mult1 = params.get("target_1_multiplier", 2.0)
            mult2 = params.get("target_2_multiplier", 3.5)
            t1 = current_price + (mock_atr * mult1)
            t2 = current_price + (mock_atr * mult2)
            cagr = 15.0
            
        elif method == "PERCENTAGE":
            pct1 = params.get("target_1_pct", 15.0)
            pct2 = params.get("target_2_pct", 25.0)
            t1 = current_price * (1.0 + (pct1 / 100.0))
            t2 = current_price * (1.0 + (pct2 / 100.0))
            cagr = pct1
            
        else: # Default RISK_REWARD
            spread_multiplier = (volatility / 100.0)
            t1 = current_price * (1.0 + (0.15 + spread_multiplier))
            t2 = current_price * (1.0 + (0.25 + spread_multiplier))
            cagr = 15.0
            
        return {
            "target_1": round(t1, 2),
            "target_2": round(t2, 2),
            "cagr": round(cagr, 2)
        }

    @staticmethod
    def calculate_stop_loss(current_price: float, volatility: float, stop_logic: Dict[str, Any]) -> float:
        """
        Executes the stop loss methodology specified in stop_logic.
        """
        method = stop_logic.get("methodology", "PERCENTAGE")
        params = stop_logic.get("params", {})
        
        if current_price <= 0: return 0.0
        
        if method == "ATR_MULTIPLIER":
            mock_atr = current_price * (volatility / 100.0) * 0.1
            mult = params.get("multiplier", 1.5)
            sl = current_price - (mock_atr * mult)
            
        elif method == "PERCENTAGE":
            pct = params.get("percentage", 10.0)
            sl = current_price * (1.0 - (pct / 100.0))
            
        elif method == "SUPPORT_BASED":
            # Mock support level
            sl = current_price * 0.85
            
        else:
            sl = current_price * 0.90
            
        return round(max(0.0, sl), 2)
