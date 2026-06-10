"""
Momentum Detector

Calculates technical indicators and momentum scores for stocks.
"""
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

class MomentumDetector:
    def __init__(self):
        self.logger = get_logger(__name__)

    def compute_momentum_score(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Computes technical indicators and returns a momentum score (0-100).
        Expects a DataFrame with columns: Open, High, Low, Close, Volume.
        """
        if df is None or len(df) < 50:
            return None
            
        try:
            # Ensure columns are properly named
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # Trend Indicators
            macd = ta.trend.MACD(close)
            macd_line = macd.macd()
            macd_signal = macd.macd_signal()
            macd_diff = macd.macd_diff()
            
            sma_20 = ta.trend.sma_indicator(close, window=20)
            sma_50 = ta.trend.sma_indicator(close, window=50)
            ema_20 = ta.trend.ema_indicator(close, window=20)
            
            # Momentum Indicators
            rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
            stoch = ta.momentum.StochasticOscillator(high, low, close).stoch()
            
            # Volatility
            bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
            bb_high = bb.bollinger_hband()
            bb_low = bb.bollinger_lband()
            
            # Current values (using last row)
            current_close = close.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_macd_diff = macd_diff.iloc[-1]
            
            # Score calculation (0 to 100)
            score = 50.0
            reasons = []
            
            # 1. RSI (Ideal between 40 and 70 for momentum, > 70 is overbought, < 30 is oversold bounce)
            if 40 <= current_rsi <= 70:
                score += 10
                reasons.append("RSI is in healthy momentum zone")
            elif current_rsi > 70:
                score -= 10
                reasons.append("RSI indicates overbought conditions")
            elif current_rsi < 30:
                score += 5
                reasons.append("RSI indicates oversold potential bounce")
                
            # 2. MACD Crossover
            if current_macd_diff > 0 and macd_diff.iloc[-2] <= 0:
                score += 15
                reasons.append("Bullish MACD Crossover")
            elif current_macd_diff > 0:
                score += 5
                reasons.append("MACD is positive")
            elif current_macd_diff < 0 and macd_diff.iloc[-2] >= 0:
                score -= 15
                reasons.append("Bearish MACD Crossover")
                
            # 3. Moving Averages (Trend)
            if current_close > sma_20.iloc[-1] > sma_50.iloc[-1]:
                score += 15
                reasons.append("Price is in strong uptrend (Above SMA20 & SMA50)")
            elif current_close < sma_20.iloc[-1] < sma_50.iloc[-1]:
                score -= 15
                reasons.append("Price is in strong downtrend")
                
            # 4. Bollinger Bands (Breakout)
            if current_close > bb_high.iloc[-1]:
                score += 5
                reasons.append("Upper Bollinger Band Breakout")
            elif current_close < bb_low.iloc[-1]:
                score -= 5
                reasons.append("Lower Bollinger Band Breakdown")
                
            # Clamp score between 0 and 100
            final_score = max(0, min(100, score))
            
            # --- Reversal / Dip-Buyer Score Calculation ---
            reversal_score = 50.0
            
            # 1. Dip from 50-day High
            highest_50 = high.rolling(window=50).max().iloc[-1]
            dip_pct = ((highest_50 - current_close) / highest_50) * 100 if highest_50 > 0 else 0
            
            if dip_pct > 15:
                reversal_score += 15
                if dip_pct > 30:
                    reversal_score += 10
            elif dip_pct < 5:
                reversal_score -= 15 # Near highs, not a dip setup
                
            # 2. RSI Recovery
            recent_rsis = rsi.iloc[-5:]
            if any(r < 35 for r in recent_rsis) and current_rsi > 35:
                reversal_score += 20
                reasons.append("RSI bounced from oversold levels")
                
            # 3. MACD Recovery
            if current_macd_diff > 0 and macd_diff.iloc[-2] <= 0:
                reversal_score += 15
            elif current_macd_diff > macd_diff.iloc[-2] and macd_diff.iloc[-2] < 0:
                reversal_score += 10 # Improving histogram while negative
                
            # 4. Short-term Price Action (higher closes)
            closes_last_3 = close.iloc[-3:]
            if closes_last_3.is_monotonic_increasing:
                reversal_score += 15
                reasons.append("Recent string of higher closes")
                
            final_reversal = max(0, min(100, reversal_score))
            
            return {
                "momentum_score": round(final_score, 2),
                "reversal_score": round(final_reversal, 2),
                "rsi": round(current_rsi, 2) if not pd.isna(current_rsi) else None,
                "macd_histogram": round(current_macd_diff, 2) if not pd.isna(current_macd_diff) else None,
                "sma_20": round(sma_20.iloc[-1], 2) if not pd.isna(sma_20.iloc[-1]) else None,
                "reasons": reasons
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compute momentum score: {e}")
            return None
