"""
VWAP Engine
Computes Volume Weighted Average Price based metrics.
"""
import pandas as pd
from typing import Dict, Any, Optional

class VWAPEngine:
    def _calc_vwap(self, df: pd.DataFrame) -> pd.Series:
        # Typical price
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        # VWAP
        vwap = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
        return vwap

    def analyze(self, df_daily: pd.DataFrame, df_intraday: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Uses intraday for true daily VWAP if available, otherwise approximates.
        Calculates anchored VWAP from the last swing low.
        """
        if df_daily is None or df_daily.empty:
            return {
                "vwap_score": 0, 
                "vwap_alignment": "Unknown", 
                "distance_to_anchored_vwap": 0,
                "distance_to_daily_vwap": 0
            }
            
        close = df_daily['Close'].iloc[-1]
        score = 50
        alignment = "Neutral"
        
        # Approximate anchored VWAP from the 20-day swing low
        recent_20 = df_daily.tail(20)
        swing_low_idx = recent_20['Low'].idxmin()
        df_anchored = df_daily.loc[swing_low_idx:].copy()
        
        if len(df_anchored) > 0 and df_anchored['Volume'].sum() > 0:
            anchored_vwap = self._calc_vwap(df_anchored).iloc[-1]
            dist_anchored = ((close - anchored_vwap) / anchored_vwap) * 100
            
            if dist_anchored > 0:
                score += 20
                alignment = "Bullish (Above Anchored VWAP)"
            elif dist_anchored < 0:
                score -= 20
                alignment = "Bearish (Below Anchored VWAP)"
        else:
            anchored_vwap = close
            dist_anchored = 0
            
        # Daily VWAP (if intraday provided, compute for the last day)
        daily_vwap = close
        dist_daily = 0
        if df_intraday is not None and not df_intraday.empty:
            # Handle timezone/index issues carefully
            last_date = df_intraday.index[-1].date()
            df_last_day = df_intraday[df_intraday.index.date == last_date].copy()
            if not df_last_day.empty and df_last_day['Volume'].sum() > 0:
                daily_vwap = self._calc_vwap(df_last_day).iloc[-1]
                dist_daily = ((close - daily_vwap) / daily_vwap) * 100
                
                if dist_daily > 0:
                    score += 30
                    if "Bullish" in alignment:
                        alignment = "Strongly Bullish (Above Daily & Anchored VWAP)"
                else:
                    score -= 10
                    
        return {
            "vwap_score": min(100, max(0, score)),
            "vwap_alignment": alignment,
            "distance_to_anchored_vwap": round(dist_anchored, 2),
            "distance_to_daily_vwap": round(dist_daily, 2)
        }
