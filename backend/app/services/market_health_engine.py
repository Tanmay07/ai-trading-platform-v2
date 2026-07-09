"""
Market Health Engine
Aggregates sub-scores into a Health Rating.
"""
from typing import Dict, Any

class MarketHealthEngine:
    def analyze(self, breadth: int, vol: int, liq: int, macro: int, inst: int) -> Dict[str, Any]:
        health = (breadth + vol + liq + macro + inst) / 5
        
        env = "Neutral"
        risk = "Moderate"
        
        if health > 80:
            env = "Excellent"
            risk = "Very Low"
        elif health > 60:
            env = "Good"
            risk = "Low"
        elif health < 40:
            env = "Poor"
            risk = "High"
        elif health < 20:
            env = "Terrible"
            risk = "Very High"
            
        return {
            "market_health_score": round(health, 2),
            "trading_environment": env,
            "risk_rating": risk
        }
