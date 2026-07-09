"""
Global Market Engine
Evaluates overnight global sentiment.
"""
import pandas as pd
from typing import Dict, Any

class GlobalMarketEngine:
    def analyze(self, df_macro: pd.DataFrame) -> Dict[str, Any]:
        if df_macro is None or df_macro.empty or getattr(df_macro.columns, 'levels', None) is None:
            return {"global_score": 50, "overnight_risk": "Unknown", "opening_bias": "Unknown"}
            
        score = 50
        
        def get_day_return(ticker: str) -> float:
            if ticker in df_macro.columns.levels[0]:
                df_t = df_macro[ticker].dropna()
                if len(df_t) > 1:
                    curr = df_t['Close'].iloc[-1]
                    prev = df_t['Close'].iloc[-2]
                    return (curr - prev) / prev
            return 0.0
            
        sp500_ret = get_day_return("^GSPC")
        dow_ret = get_day_return("^DJI")
        nikkei_ret = get_day_return("^N225")
        
        # Simple scoring based on overnight % returns
        if sp500_ret > 0: score += 10
        else: score -= 10
            
        if dow_ret > 0: score += 10
        else: score -= 10
            
        if nikkei_ret > 0: score += 10
        else: score -= 10
        
        score = max(0, min(100, score))
        
        if score > 60:
            bias = "Positive"
            risk = "Low"
        elif score < 40:
            bias = "Negative"
            risk = "High"
        else:
            bias = "Neutral"
            risk = "Moderate"
            
        return {
            "global_score": score,
            "overnight_risk": risk,
            "opening_bias": bias,
            "sp500_return": round(float(sp500_ret * 100), 2),
            "nikkei_return": round(float(nikkei_ret * 100), 2)
        }
