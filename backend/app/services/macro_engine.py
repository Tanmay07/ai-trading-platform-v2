"""
Macro Engine
Evaluates macroeconomic indicators.
"""
import pandas as pd
from typing import Dict, Any

class MacroEngine:
    def analyze(self, df_macro: pd.DataFrame) -> Dict[str, Any]:
        """
        df_macro contains multi-index columns with tickers:
        ^INDIAVIX, INR=X, DX-Y.NYB, ^TNX, BZ=F, GC=F
        """
        if df_macro is None or df_macro.empty or getattr(df_macro.columns, 'levels', None) is None:
            return {"macro_score": 50, "risk_level": "Unknown", "global_sentiment": "Unknown"}
            
        score = 50
        
        def get_trend(ticker: str) -> int:
            if ticker in df_macro.columns.levels[0]:
                df_t = df_macro[ticker].dropna()
                if len(df_t) > 20:
                    curr = df_t['Close'].iloc[-1]
                    sma20 = df_t['Close'].rolling(20).mean().iloc[-1]
                    return 1 if curr > sma20 else -1
            return 0
            
        # VIX going up is bad
        vix_trend = get_trend("^INDIAVIX")
        if vix_trend == 1: score -= 15
        elif vix_trend == -1: score += 10
        
        # USD/INR going up is bad for Indian markets
        usdinr_trend = get_trend("INR=X")
        if usdinr_trend == 1: score -= 10
        elif usdinr_trend == -1: score += 10
        
        # DXY going up is bad for emerging markets
        dxy_trend = get_trend("DX-Y.NYB")
        if dxy_trend == 1: score -= 10
        elif dxy_trend == -1: score += 10
        
        # US 10Y going up is bad for equities
        tnx_trend = get_trend("^TNX")
        if tnx_trend == 1: score -= 10
        elif tnx_trend == -1: score += 10
        
        # Brent going up is bad for India (importer)
        brent_trend = get_trend("BZ=F")
        if brent_trend == 1: score -= 10
        elif brent_trend == -1: score += 10
        
        score = max(0, min(100, score))
        
        if score >= 70:
            risk = "Low"
            sentiment = "Bullish"
        elif score <= 30:
            risk = "High"
            sentiment = "Bearish"
        else:
            risk = "Moderate"
            sentiment = "Neutral"
            
        return {
            "macro_score": score,
            "risk_level": risk,
            "global_sentiment": sentiment,
            "vix_trend": "Up" if vix_trend == 1 else ("Down" if vix_trend == -1 else "Neutral"),
            "usdinr_trend": "Up" if usdinr_trend == 1 else ("Down" if usdinr_trend == -1 else "Neutral"),
            "dxy_trend": "Up" if dxy_trend == 1 else ("Down" if dxy_trend == -1 else "Neutral"),
            "us10y_trend": "Up" if tnx_trend == 1 else ("Down" if tnx_trend == -1 else "Neutral"),
            "brent_trend": "Up" if brent_trend == 1 else ("Down" if brent_trend == -1 else "Neutral")
        }
