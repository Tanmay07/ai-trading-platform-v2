"""
Market Breadth Engine
Calculates daily market breadth indicators based on the candidate universe.
"""
import pandas as pd
from typing import Dict, Any

class MarketBreadthEngine:
    def analyze(self, df_all: pd.DataFrame) -> Dict[str, Any]:
        """
        df_all should be a MultiIndex dataframe with tickers on level 0 (from yfinance).
        """
        if df_all is None or df_all.empty or getattr(df_all.columns, 'levels', None) is None:
            return {"breadth_score": 50, "breadth_trend": "Unknown", "ad_ratio": 1}
            
        tickers = df_all.columns.levels[0]
        
        advances = 0
        declines = 0
        above_20 = 0
        above_50 = 0
        above_200 = 0
        new_highs = 0
        new_lows = 0
        
        valid_tickers = 0
        
        for t in tickers:
            if 'Close' not in df_all[t]:
                continue
                
            df = df_all[t].dropna()
            if len(df) < 200:
                continue
                
            valid_tickers += 1
            close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            
            if close > prev_close:
                advances += 1
            elif close < prev_close:
                declines += 1
                
            ema20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
            
            if close > ema20: above_20 += 1
            if close > ema50: above_50 += 1
            if close > ema200: above_200 += 1
            
            high_52 = df['High'].tail(252).max()
            low_52 = df['Low'].tail(252).min()
            if df['High'].iloc[-1] >= high_52: new_highs += 1
            if df['Low'].iloc[-1] <= low_52: new_lows += 1
            
        if valid_tickers == 0:
            return {"breadth_score": 50, "breadth_trend": "Unknown", "ad_ratio": 1}
            
        pct_20 = (above_20 / valid_tickers) * 100
        pct_50 = (above_50 / valid_tickers) * 100
        pct_200 = (above_200 / valid_tickers) * 100
        ad_ratio = advances / declines if declines > 0 else advances
        
        # Simple scoring
        score = 0
        if ad_ratio > 1.0: score += 20
        if ad_ratio > 2.0: score += 10
        if pct_20 > 50: score += 20
        if pct_50 > 50: score += 20
        if pct_200 > 50: score += 30
        
        trend = "Neutral"
        if score > 70:
            trend = "Bullish"
        elif score < 30:
            trend = "Bearish"
            
        return {
            "breadth_score": score,
            "breadth_trend": trend,
            "breadth_strength": score,
            "advances": advances,
            "declines": declines,
            "ad_ratio": round(float(ad_ratio), 2),
            "pct_above_20_ema": round(float(pct_20), 2),
            "pct_above_50_ema": round(float(pct_50), 2),
            "pct_above_200_ema": round(float(pct_200), 2),
            "new_52w_highs": new_highs,
            "new_52w_lows": new_lows
        }
