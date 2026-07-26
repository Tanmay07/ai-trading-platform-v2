from typing import Dict, Any

class HealthAnalytics:
    @staticmethod
    def calculate_health_score(allocations: Dict[str, Any], risk_metrics: Dict[str, Any]) -> float:
        """
        Calculates a 0-100 score based on portfolio diversification, concentration, and risk.
        Placeholder implementation.
        """
        score = 100.0
        
        # Penalty for high concentration in single stock (>20%)
        stock_alloc = allocations.get("stock", {})
        for weight in stock_alloc.values():
            if weight > 20.0:
                score -= (weight - 20.0) * 1.5

        # Cap score between 0 and 100
        return max(0.0, min(100.0, score))
