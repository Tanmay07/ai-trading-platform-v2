"""
Support & Resistance Engine
Detects horizontal levels and swing points.
"""
import pandas as pd
from typing import Dict, Any

class SupportResistanceEngine:
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {
                "support": 0, 
                "resistance": 0, 
                "distance_to_support": 0, 
                "distance_to_resistance": 0
            }
            
        close = df['Close'].iloc[-1]
        
        # Simple swing detection (highest high in last 20 days, lowest low in last 20 days)
        recent = df.tail(20)
        swing_high = recent['High'].max()
        swing_low = recent['Low'].min()
        
        # Simplified horizontal level detection using older data to find valid S/R if current price is breaking out
        if recent['High'].iloc[-1] == swing_high:
            # Current is highest, look back further for resistance
            older = df.iloc[-60:-1]
            resistance = older['High'].max() if len(older) > 0 else swing_high
        else:
            resistance = swing_high
            
        if recent['Low'].iloc[-1] == swing_low:
            older = df.iloc[-60:-1]
            support = older['Low'].min() if len(older) > 0 else swing_low
        else:
            support = swing_low
            
        dist_sup = ((close - support) / support) * 100 if support > 0 else 0
        dist_res = ((resistance - close) / close) * 100 if close > 0 else 0
        
        return {
            "support_level": round(float(support), 2),
            "resistance_level": round(float(resistance), 2),
            "distance_to_support": round(float(dist_sup), 2),
            "distance_to_resistance": round(float(dist_res), 2)
        }
