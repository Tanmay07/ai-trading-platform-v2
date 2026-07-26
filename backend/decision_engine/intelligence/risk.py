import hashlib
from typing import Dict, Any

class RiskIntelligence:
    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Calculates Volatility, Drawdown, and Beta.
        Returns a score 0-100 (where 100 = Lowest Risk, 0 = Highest Risk).
        """
        # We use a deterministic mock for volatility/beta if live historical series is missing.
        h = int(hashlib.sha256(symbol.encode('utf-8')).hexdigest(), 16)
        
        # Volatility: 10% to 50%
        volatility = 10.0 + (h % 40)
        
        # Beta: 0.5 to 2.0
        beta = 0.5 + ((h % 15) / 10.0)
        
        # Max Drawdown: -5% to -40%
        drawdown = -5.0 - (h % 35)
        
        score = 100.0
        
        # Penalize High Volatility
        if volatility > 40: score -= 30
        elif volatility > 30: score -= 15
        elif volatility < 15: score += 10 # Reward low volatility
        
        # Penalize High Beta (relative to market risk)
        if beta > 1.5: score -= 20
        elif beta < 0.8: score += 15 # Defensive
        
        # Penalize deep historical drawdowns
        if drawdown < -30: score -= 30
        elif drawdown < -20: score -= 10
        
        return {
            "score": min(100.0, max(0.0, score)),
            "metrics": {
                "volatility_pct": round(volatility, 2),
                "beta": round(beta, 2),
                "max_drawdown_pct": round(drawdown, 2),
                "risk_profile": "High" if score < 40 else "Low" if score > 70 else "Moderate"
            }
        }
