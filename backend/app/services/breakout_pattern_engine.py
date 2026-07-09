"""
Institutional Breakout Pattern Engine
Detects VCP, NR7, Inside Bar, etc.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from app.config_technical import technical_config

class BreakoutPatternEngine:
    def __init__(self):
        self.config = technical_config.pattern_thresholds

    def _detect_nr7(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Narrow Range 7 (NR7) detection"""
        if len(df) < 7:
            return None
            
        recent_7 = df.tail(7)
        ranges = recent_7['High'] - recent_7['Low']
        
        # If the last day has the smallest range of the last 7 days
        if ranges.iloc[-1] == ranges.min() and ranges.iloc[-1] > 0:
            return {
                "Pattern_Name": "NR7",
                "Pattern_Quality": 80,
                "Breakout_Level": float(recent_7['High'].iloc[-1]),
                "Pattern_Age": 7,
                "Confidence": 75
            }
        return None

    def _detect_inside_bar(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        if len(df) < 2:
            return None
            
        recent = df.tail(2)
        prev_high, prev_low = recent['High'].iloc[0], recent['Low'].iloc[0]
        curr_high, curr_low = recent['High'].iloc[-1], recent['Low'].iloc[-1]
        
        if curr_high < prev_high and curr_low > prev_low:
            return {
                "Pattern_Name": "Inside Bar",
                "Pattern_Quality": 70,
                "Breakout_Level": float(prev_high),
                "Pattern_Age": 2,
                "Confidence": 65
            }
        return None
        
    def _detect_vcp(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Simplified Volatility Contraction Pattern (VCP)"""
        # Look for decreasing volume and tightening price ranges over last 20 days
        if len(df) < 20:
            return None
            
        recent = df.tail(20)
        range_5 = (recent['High'].tail(5).max() - recent['Low'].tail(5).min()) / recent['Low'].tail(5).min() * 100
        range_15 = (recent['High'].head(15).max() - recent['Low'].head(15).min()) / recent['Low'].head(15).min() * 100
        
        if range_5 < self.config.vcp_max_contraction_percent and range_5 < (range_15 * 0.5):
            # Volume contraction check
            vol_5 = recent['Volume'].tail(5).mean()
            vol_15 = recent['Volume'].head(15).mean()
            
            if vol_5 < vol_15:
                return {
                    "Pattern_Name": "Volatility Contraction Pattern",
                    "Pattern_Quality": 95,
                    "Breakout_Level": float(recent['High'].tail(5).max()),
                    "Pattern_Age": 20,
                    "Confidence": 90
                }
        return None
        
    def analyze(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analyzes the dataframe and returns a list of detected patterns.
        """
        if df is None or df.empty:
            return []
            
        patterns = []
        
        vcp = self._detect_vcp(df)
        if vcp: patterns.append(vcp)
            
        nr7 = self._detect_nr7(df)
        if nr7: patterns.append(nr7)
            
        ib = self._detect_inside_bar(df)
        if ib: patterns.append(ib)
            
        # Return sorted by quality
        patterns.sort(key=lambda x: x["Pattern_Quality"], reverse=True)
        return patterns
