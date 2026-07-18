from typing import List, Dict, Any

class PortfolioMetrics:
    @staticmethod
    def calculate_health_score(portfolio: List[Dict[str, Any]], rejected: List[Dict[str, Any]]) -> float:
        """
        Calculates a 0-100 score representing the structural health and AI confidence of the portfolio.
        """
        if not portfolio:
             return 0.0
             
        avg_trade_quality = sum(p.get("trade_quality_prediction", 50) for p in portfolio) / len(portfolio)
        avg_confidence = sum(p.get("confidence", 0.5) for p in portfolio) / len(portfolio)
        
        # Sector diversification bonus
        sectors = set(p.get("sector", "Unknown") for p in portfolio)
        div_bonus = min(len(sectors) * 2.5, 20) # Up to 20 pts for having 8+ sectors
        
        score = (avg_trade_quality * 0.5) + (avg_confidence * 100 * 0.3) + div_bonus
        return min(max(score, 0), 100)
        
    @staticmethod
    def get_sector_exposure(portfolio: List[Dict[str, Any]]) -> Dict[str, float]:
        exposure = {}
        total_weight = sum(p.get("weight", 0) for p in portfolio)
        if total_weight == 0:
            return exposure
            
        for p in portfolio:
             sec = p.get("sector", "Unknown")
             exposure[sec] = exposure.get(sec, 0) + (p.get("weight", 0) / total_weight)
             
        return exposure
