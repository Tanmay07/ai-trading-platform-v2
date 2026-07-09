from typing import Dict, Any
from app.portfolio.exposure_engine import ExposureEngine
from app.portfolio.kelly_optimizer import KellyOptimizer

class AllocationEngine:
    def __init__(self):
        self.exposure_engine = ExposureEngine()
        self.kelly_optimizer = KellyOptimizer()

    def allocate(self, current_portfolio: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the final allocation amount in currency, based on Kelly limits and Exposure limits.
        """
        kelly_fraction = self.kelly_optimizer.calculate_kelly_fraction(candidate)
        max_exposure_allowed = self.exposure_engine.get_max_allocation(current_portfolio, candidate)
        
        final_allocation_pct = min(kelly_fraction, max_exposure_allowed)
        
        cash_available = current_portfolio.get("cash", 0.0)
        total_value = current_portfolio.get("total_value", 1.0)
        
        target_allocation_cash = total_value * final_allocation_pct
        
        # Can't allocate more than we have
        actual_allocation_cash = min(target_allocation_cash, cash_available)
        
        return {
            "kelly_fraction": kelly_fraction,
            "max_exposure_allowed": round(max_exposure_allowed, 4),
            "final_allocation_pct": round(actual_allocation_cash / total_value, 4),
            "final_allocation_cash": round(actual_allocation_cash, 2)
        }
