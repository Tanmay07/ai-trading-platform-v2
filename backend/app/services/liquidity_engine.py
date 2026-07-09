"""
Liquidity Engine
Measures market-wide liquidity based on volume trends.
"""
import pandas as pd
from typing import Dict, Any

class LiquidityEngine:
    def analyze(self, df_all: pd.DataFrame) -> Dict[str, Any]:
        """
        Uses the multi-index dataframe of the universe to assess overall volume.
        """
        if df_all is None or df_all.empty or getattr(df_all.columns, 'levels', None) is None:
            return {"liquidity_score": 50, "liquidity_trend": "Unknown", "volume_ratio": 1.0}
            
        tickers = df_all.columns.levels[0]
        
        total_vol_today = 0
        total_vol_avg = 0
        
        for t in tickers:
            if 'Volume' not in df_all[t]:
                continue
            df = df_all[t].dropna()
            if len(df) < 20:
                continue
                
            total_vol_today += df['Volume'].iloc[-1]
            total_vol_avg += df['Volume'].rolling(20).mean().iloc[-1]
            
        if total_vol_avg == 0:
            return {"liquidity_score": 50, "liquidity_trend": "Unknown", "volume_ratio": 1.0}
            
        ratio = total_vol_today / total_vol_avg
        
        score = 50
        if ratio > 1.2:
            score = 80
            trend = "Expanding"
        elif ratio > 0.9:
            score = 60
            trend = "Stable"
        elif ratio > 0.7:
            score = 40
            trend = "Contracting"
        else:
            score = 20
            trend = "Drying Up"
            
        return {
            "liquidity_score": score,
            "liquidity_trend": trend,
            "volume_ratio": round(float(ratio), 2)
        }
