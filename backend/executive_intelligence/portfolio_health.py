import logging
from typing import Dict, Any

logger = logging.getLogger("PortfolioHealth")

class PortfolioHealthEngine:
    """
    Computes a 0-100 score of overall portfolio health.
    """
    def __init__(self):
        pass
        
    def calculate_health(self, risk_metrics: Dict[str, Any], cash_ratio: float) -> Dict[str, Any]:
        """
        Takes risk metrics and computes a composite health score.
        """
        score = 100.0
        deductions = []
        
        # 1. Volatility check
        vol = risk_metrics.get('portfolio_volatility', 0)
        if vol > 0.40:
            score -= 20
            deductions.append("High portfolio volatility (>40%)")
        elif vol > 0.25:
            score -= 10
            deductions.append("Elevated portfolio volatility (>25%)")
            
        # 2. Diversification check
        div = risk_metrics.get('diversification_score', 100)
        if div < 50:
            score -= 15
            deductions.append("Poor sector diversification")
        elif div < 75:
            score -= 5
            deductions.append("Sub-optimal diversification")
            
        # 3. Cash check
        if cash_ratio < 0.05:
            score -= 10
            deductions.append("Low cash reserves (<5%)")
            
        score = max(0.0, score)
        
        grade = "A"
        if score < 60: grade = "D"
        elif score < 75: grade = "C"
        elif score < 90: grade = "B"
        
        return {
            "health_score": score,
            "grade": grade,
            "deductions": deductions,
            "status": "Healthy" if score >= 80 else "Needs Attention"
        }
