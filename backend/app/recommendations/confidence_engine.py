"""
Confidence Scoring Engine
"""
import pandas as pd
from typing import Dict, Any
from app.config_yaml import trading_config

class ConfidenceEngine:
    def __init__(self):
        self.weights = trading_config.confidence_weights

    def _score_trend(self, row: pd.Series) -> tuple[float, str]:
        score = 0
        reasons = []
        
        price = row.get("Close", 0)
        ema20 = row.get("ema_20", 0)
        ema50 = row.get("ema_50", 0)
        ema200 = row.get("ema_200", 0)
        
        if price > ema20:
            score += 25
        if ema20 > ema50:
            score += 25
            reasons.append("EMA Alignment (20>50)")
        if price > ema200:
            score += 50
            reasons.append("Long-term Trend Bullish")
            
        return score, ", ".join(reasons)

    def _score_volume(self, row: pd.Series, df: pd.DataFrame) -> tuple[float, str]:
        score = 0
        reasons = []
        
        # Calculate relative volume if not present
        if "Volume" in row and df is not None and not df.empty:
            vol_sma = df["Volume"].tail(20).mean()
            rel_vol = row["Volume"] / vol_sma if vol_sma > 0 else 1
        else:
            rel_vol = row.get("relative_volume", 1)
            
        if rel_vol > 1.5:
            score += 60
            reasons.append(f"High Relative Volume ({rel_vol:.1f}x)")
        elif rel_vol > 1.0:
            score += 30
            
        # OBV trend (simplified check if latest OBV is higher than 5 days ago)
        if "obv" in df.columns and len(df) > 5:
            if df["obv"].iloc[-1] > df["obv"].iloc[-5]:
                score += 40
                reasons.append("OBV Trending Up")
                
        return min(100, score), ", ".join(reasons)

    def _score_momentum(self, row: pd.Series) -> tuple[float, str]:
        score = 0
        reasons = []
        
        rsi = row.get("rsi_14", 50)
        if 50 < rsi < 70:
            score += 40
            reasons.append("Bullish RSI Zone")
        elif rsi >= 70:
            score += 20 # Overbought, but strong momentum
            
        macd = row.get("macd", 0)
        macd_signal = row.get("macd_signal", 0)
        
        if macd > macd_signal:
            score += 40
            reasons.append("MACD Bullish Cross")
            
        adx = row.get("adx_14", 0)
        if adx > 25:
            score += 20
            reasons.append("Strong ADX Trend")
            
        return min(100, score), ", ".join(reasons)
        
    def _score_volatility(self, row: pd.Series, df: pd.DataFrame) -> tuple[float, str]:
        score = 0
        reasons = []
        
        bb_width = row.get("bb_bandwidth", 0)
        
        # If BB bandwidth is expanding (current > 5-day SMA of width)
        if "bb_bandwidth" in df.columns and len(df) > 5:
            bb_width_sma = df["bb_bandwidth"].tail(5).mean()
            if bb_width > bb_width_sma:
                score += 50
                reasons.append("Volatility Expansion")
            else:
                score += 100 # Low volatility contraction is also good for entry
                reasons.append("Volatility Contraction (Squeeze)")
                
        return min(100, score), ", ".join(reasons)

    def generate_confidence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates a 0-100 confidence score based on technical structure.
        """
        if df.empty:
            return {"confidence": 0, "grade": "F", "reason": "No data"}
            
        latest = df.iloc[-1]
        
        trend_score, trend_reason = self._score_trend(latest)
        vol_score, vol_reason = self._score_volume(latest, df)
        mom_score, mom_reason = self._score_momentum(latest)
        vty_score, vty_reason = self._score_volatility(latest, df)
        
        final_score = (
            (trend_score * self.weights.trend) +
            (vol_score * self.weights.volume) +
            (mom_score * self.weights.momentum) +
            (vty_score * self.weights.volatility)
        )
        final_score = min(100, max(0, round(final_score)))
        
        # Grade logic
        if final_score >= 90:
            grade = "A+"
        elif final_score >= 80:
            grade = "A"
        elif final_score >= 70:
            grade = "B"
        elif final_score >= 60:
            grade = "C"
        else:
            grade = "D"
            
        reasons = [r for r in [trend_reason, vol_reason, mom_reason, vty_reason] if r]
        
        return {
            "confidence": final_score,
            "grade": grade,
            "trend_score": round(trend_score),
            "volume_score": round(vol_score),
            "momentum_score": round(mom_score),
            "volatility_score": round(vty_score),
            "reason_summary": " | ".join(reasons) if reasons else "No clear structural edge."
        }
