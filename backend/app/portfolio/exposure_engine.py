from typing import Dict, Any
from app.config_portfolio import portfolio_config

class ExposureEngine:
    def get_max_allocation(self, current_portfolio: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """
        Calculates the maximum allowable percentage allocation for this candidate based on limits.
        """
        holdings = current_portfolio.get("holdings", {})
        total_value = current_portfolio.get("total_value", 1.0)
        
        sector = candidate.get("Sector", "Unknown")
        current_sector_value = sum(
            data.get("value", 0.0) 
            for ticker, data in holdings.items() 
            if data.get("sector") == sector
        )
        
        current_sector_pct = current_sector_value / total_value
        max_sector_pct = portfolio_config.limits.max_sector_exposure
        
        allowed_by_sector = max(0.0, max_sector_pct - current_sector_pct)
        allowed_by_stock = portfolio_config.limits.max_stock_allocation
        
        return min(allowed_by_sector, allowed_by_stock)
