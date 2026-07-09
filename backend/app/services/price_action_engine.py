"""
Price Action Engine
Analyzes raw price structure and candlesticks independent of indicators.
"""
import pandas as pd
from typing import Dict, Any

class PriceActionEngine:
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 5:
            return {
                "price_action_score": 0, 
                "trend_quality": "Unknown", 
                "candle_strength": "None", 
                "reversal_probability": 0
            }
            
        score = 50
        trend_quality = "Neutral"
        candle = "Neutral"
        reversal_prob = 0
        
        recent = df.tail(5)
        
        # Trend Structure (Higher Highs / Higher Lows)
        hh = recent['High'].iloc[-1] > recent['High'].iloc[-2]
        hl = recent['Low'].iloc[-1] > recent['Low'].iloc[-2]
        lh = recent['High'].iloc[-1] < recent['High'].iloc[-2]
        ll = recent['Low'].iloc[-1] < recent['Low'].iloc[-2]
        
        if hh and hl:
            trend_quality = "Bullish (HH, HL)"
            score += 20
        elif lh and ll:
            trend_quality = "Bearish (LH, LL)"
            score -= 20
            
        # Candlestick
        prev_open, prev_close = recent['Open'].iloc[-2], recent['Close'].iloc[-2]
        curr_open, curr_close = recent['Open'].iloc[-1], recent['Close'].iloc[-1]
        
        # Bullish Engulfing
        if prev_close < prev_open and curr_close > curr_open:
            if curr_open <= prev_close and curr_close >= prev_open:
                candle = "Bullish Engulfing"
                score += 30
                reversal_prob = 70
                
        # Bearish Engulfing
        elif prev_close > prev_open and curr_close < curr_open:
            if curr_open >= prev_close and curr_close <= prev_open:
                candle = "Bearish Engulfing"
                score -= 30
                reversal_prob = 80
                
        # Marubozu (strong close)
        curr_range = recent['High'].iloc[-1] - recent['Low'].iloc[-1]
        if curr_range > 0:
            if (curr_close - recent['Low'].iloc[-1]) / curr_range > 0.9 and curr_close > curr_open:
                if candle == "Neutral":
                    candle = "Bullish Marubozu"
                score += 15
                
        score = min(100, max(0, score))
        
        return {
            "price_action_score": score,
            "trend_quality": trend_quality,
            "candle_strength": candle,
            "reversal_probability": reversal_prob
        }
