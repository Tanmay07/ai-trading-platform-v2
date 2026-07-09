"""
Volatility Engine
Evaluates market volatility.
"""
import pandas as pd
from typing import Dict, Any

class VolatilityEngine:
    def analyze(self, df_vix: pd.DataFrame) -> Dict[str, Any]:
        score = 50
        state = "Normal"
        reliability = "Moderate"
        
        if df_vix is None or df_vix.empty:
            return {
                "volatility_score": score,
                "volatility_state": state,
                "breakout_reliability": reliability
            }
            
        vix = df_vix['Close'].iloc[-1]
        vix_sma20 = df_vix['Close'].rolling(20).mean().iloc[-1]
        
        # Volatility Regimes based on India VIX
        if vix > 22:
            state = "Extreme Volatility"
            score = 20
            reliability = "Very Low"
        elif vix > 18:
            state = "High Volatility"
            score = 40
            reliability = "Low"
        elif vix < 13:
            state = "Low Volatility"
            score = 80
            reliability = "High"
        else:
            state = "Normal Volatility"
            score = 60
            reliability = "Moderate"
            
        # VIX trend
        if vix > vix_sma20:
            score -= 15
        else:
            score += 15
            
        score = max(0, min(100, score))
        
        return {
            "volatility_score": score,
            "volatility_state": state,
            "breakout_reliability": reliability,
            "current_vix": round(float(vix), 2)
        }
