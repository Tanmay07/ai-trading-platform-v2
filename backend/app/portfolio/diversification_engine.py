from typing import Dict, Any

class DiversificationEngine:
    def evaluate_impact(self, current_portfolio: Dict[str, Any], candidate_sector: str) -> float:
        """
        Returns a score representing how much diversification improves.
        Positive = improves, Negative = hurts (concentrates).
        """
        # Simplified logic
        holdings = current_portfolio.get("holdings", {})
        existing_sectors = [data.get("sector") for data in holdings.values()]
        
        if candidate_sector in existing_sectors:
            return -0.05 # Slightly hurts diversification
        return 0.10 # Improves diversification
