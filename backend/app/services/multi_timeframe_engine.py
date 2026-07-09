"""
Multi-Timeframe Analysis Engine
Evaluates Weekly, Daily, 4H, and 1H data to generate a composite score.
"""
import pandas as pd
from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MultiTimeframeEngine:
    def __init__(self):
        pass

    def _calc_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        return df['Close'].ewm(span=period, adjust=False).mean()

    def _evaluate_weekly(self, df: pd.DataFrame) -> tuple[float, str]:
        if df is None or len(df) < 200:
            return 0, "Insufficient Weekly Data"
            
        score = 0
        reasons = []
        
        close = df['Close'].iloc[-1]
        
        # Calculate EMAs manually if not provided in the raw df
        ema20 = self._calc_ema(df, 20).iloc[-1]
        ema50 = self._calc_ema(df, 50).iloc[-1]
        ema200 = self._calc_ema(df, 200).iloc[-1]
        
        if close > ema20:
            score += 20
        if close > ema50:
            score += 20
        if close > ema200:
            score += 30
            reasons.append("Strong LT Trend")
            
        # Higher Highs / Higher Lows (simplified over last 4 weeks)
        recent = df.tail(4)
        if recent['Close'].iloc[-1] > recent['Close'].iloc[0]:
            score += 30
            reasons.append("Weekly Higher Highs")
            
        return score, ", ".join(reasons)

    def _evaluate_daily(self, df: pd.DataFrame) -> tuple[float, str]:
        if df is None or len(df) < 50:
            return 0, "Insufficient Daily Data"
            
        score = 0
        reasons = []
        
        # Assume daily df has EMAs from FeaturePipeline, but if not calculate them
        ema20 = self._calc_ema(df, 20).iloc[-1]
        ema50 = self._calc_ema(df, 50).iloc[-1]
        close = df['Close'].iloc[-1]
        
        if close > ema20 > ema50:
            score += 40
            reasons.append("Daily EMA Alignment")
            
        # Volume expansion
        vol_sma = df['Volume'].tail(20).mean()
        if df['Volume'].iloc[-1] > vol_sma * 1.5:
            score += 30
            reasons.append("Daily Volume Expansion")
            
        # Consolidation (BB bandwidth or simple tight range)
        recent_max = df['High'].tail(10).max()
        recent_min = df['Low'].tail(10).min()
        if recent_min > 0 and (recent_max - recent_min) / recent_min < 0.05:
            score += 30
            reasons.append("Tight Consolidation")
            
        return score, ", ".join(reasons)

    def _evaluate_4h(self, df: pd.DataFrame) -> tuple[float, str]:
        if df is None or len(df) < 20:
            return 0, "Insufficient 4H Data"
            
        score = 0
        reasons = []
        
        ema20 = self._calc_ema(df, 20).iloc[-1]
        close = df['Close'].iloc[-1]
        
        if close > ema20:
            score += 50
            reasons.append("4H Bullish Trend")
            
        # Pullback check (if close is near EMA20)
        if 0 < (close - ema20) / ema20 < 0.02:
            score += 50
            reasons.append("4H Pullback Entry")
            
        return score, ", ".join(reasons)

    def _evaluate_1h(self, df: pd.DataFrame) -> tuple[float, str]:
        if df is None or len(df) < 10:
            return 0, "Insufficient 1H Data"
            
        score = 0
        reasons = []
        
        # Momentum acceleration / breakout candle
        recent_2 = df.tail(2)
        if recent_2['Close'].iloc[-1] > recent_2['High'].iloc[0]:
            score += 50
            reasons.append("1H Breakout Candle")
            
        # Volume spike on 1H
        vol_sma = df['Volume'].tail(10).mean()
        if df['Volume'].iloc[-1] > vol_sma * 2.0:
            score += 50
            reasons.append("1H Volume Spike")
            
        return score, ", ".join(reasons)

    def analyze(self, dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Expects dfs to contain keys: '1wk', '1d', '4h', '1h'
        """
        wk_score, wk_reason = self._evaluate_weekly(dfs.get('1wk'))
        d_score, d_reason = self._evaluate_daily(dfs.get('1d'))
        h4_score, h4_reason = self._evaluate_4h(dfs.get('4h'))
        h1_score, h1_reason = self._evaluate_1h(dfs.get('1h'))
        
        # Composite score
        mtf_score = (wk_score * 0.4) + (d_score * 0.3) + (h4_score * 0.2) + (h1_score * 0.1)
        
        return {
            "weekly_score": round(wk_score, 2),
            "weekly_trend": wk_reason,
            "daily_score": round(d_score, 2),
            "daily_trend": d_reason,
            "4h_score": round(h4_score, 2),
            "4h_trend": h4_reason,
            "1h_score": round(h1_score, 2),
            "1h_trend": h1_reason,
            "mtf_score": round(mtf_score, 2)
        }
