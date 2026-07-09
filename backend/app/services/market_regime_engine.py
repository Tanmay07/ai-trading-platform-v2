"""
Market Regime Engine
Classifies the current market environment.
"""
import pandas as pd
from typing import Dict, Any
from app.config_market import market_config

class MarketRegimeEngine:
    def _calc_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        return df['Close'].ewm(span=period, adjust=False).mean()

    def analyze(self, df_market: pd.DataFrame) -> Dict[str, Any]:
        if df_market is None or len(df_market) < 200:
            return {
                "regime": "Unknown",
                "regime_score": 50,
                "confidence": 0,
                "exposure_multiplier": 0.5,
                "breakout_success_rate": 50
            }
            
        close = df_market['Close'].iloc[-1]
        ema20 = self._calc_ema(df_market, 20).iloc[-1]
        ema50 = self._calc_ema(df_market, 50).iloc[-1]
        ema200 = self._calc_ema(df_market, 200).iloc[-1]
        
        regime = "Sideways"
        score = 50
        conf = 50
        success_rate = 50
        
        if close > ema20 > ema50 > ema200:
            regime = "Strong Bull"
            score = 95
            conf = 90
            success_rate = 80
        elif close > ema50 > ema200:
            regime = "Bull"
            score = 80
            conf = 80
            success_rate = 65
        elif close > ema200 and (close < ema50 or close < ema20):
            regime = "Weak Bull"
            score = 65
            conf = 70
            success_rate = 55
        elif ema200 > close > ema50:
            regime = "Accumulation"
            score = 60
            conf = 60
            success_rate = 50
        elif close < ema20 < ema50 < ema200:
            regime = "Bear"
            score = 10
            conf = 90
            success_rate = 20
        elif close < ema50 < ema200:
            regime = "Bear"
            score = 25
            conf = 80
            success_rate = 30
        elif close < ema200:
            regime = "Weak Bear"
            score = 40
            conf = 70
            success_rate = 40
            
        exposure = market_config.exposure_rules.get(regime, 0.5)
        
        return {
            "regime": regime,
            "regime_score": score,
            "confidence": conf,
            "exposure_multiplier": exposure,
            "breakout_success_rate": success_rate
        }
