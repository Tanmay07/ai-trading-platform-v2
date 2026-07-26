import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TechnicalEngine:
    """
    Calculates technical analysis indicators for a given company.
    In a real system, this would load historical price bars and calculate indicators using pandas-ta or talib.
    For this MVP, it generates realistic mock data based on recent price action logic.
    """
    
    def analyze(self, symbol: str, current_price: float = None) -> Dict[str, Any]:
        logger.info(f"Running Technical Analysis for {symbol}")
        
        random.seed(hash(symbol) + 1)
        
        cp = current_price if current_price else random.uniform(50, 5000)
        
        # Technicals
        rsi = random.uniform(20, 85)
        macd = random.uniform(-5, 15)
        adx = random.uniform(10, 50)
        
        # Support/Resistance relative to CP
        support = cp * random.uniform(0.85, 0.95)
        resistance = cp * random.uniform(1.05, 1.15)
        
        trend = "Bullish"
        if rsi < 40 and macd < 0:
            trend = "Bearish"
        elif rsi > 40 and rsi < 60:
            trend = "Neutral"
            
        score = 50
        
        if trend == "Bullish": score += 15
        elif trend == "Bearish": score -= 15
        
        if rsi > 70: score -= 10 # Overbought
        elif rsi < 30: score += 10 # Oversold
        
        if adx > 25: 
            score += 10 if trend == "Bullish" else -10
            
        score = max(0, min(100, score))
        
        return {
            "trend": trend,
            "rsi": round(rsi, 2),
            "macd": round(macd, 2),
            "adx": round(adx, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "ema_50": round(cp * random.uniform(0.9, 1.1), 2),
            "sma_200": round(cp * random.uniform(0.8, 1.2), 2),
            "volume_trend": random.choice(["Accumulation", "Distribution", "Neutral"]),
            "bollinger_band": random.choice(["Upper", "Middle", "Lower"]),
            "breakout_detection": random.choice(["None", "Resistance Breakout", "Support Breakdown"]),
            "technical_score": round(score, 2)
        }
