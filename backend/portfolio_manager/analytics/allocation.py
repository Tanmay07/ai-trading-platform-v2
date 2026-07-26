from typing import List, Dict, Any
from portfolio_manager.schemas import HoldingResponse

class AllocationAnalytics:
    @staticmethod
    def get_allocations(holdings: List[HoldingResponse]) -> Dict[str, Any]:
        total_value = sum(h.current_value for h in holdings if h.current_value)
        if total_value <= 0:
            return {}

        sector_allocation = {}
        industry_allocation = {}
        market_cap_allocation = {}
        stock_allocation = {}

        for h in holdings:
            val = h.current_value or 0.0
            weight = (val / total_value) * 100

            sector = h.sector or "Unknown"
            sector_allocation[sector] = sector_allocation.get(sector, 0) + weight

            industry = h.industry or "Unknown"
            industry_allocation[industry] = industry_allocation.get(industry, 0) + weight

            stock_allocation[h.symbol] = weight

        return {
            "sector": sector_allocation,
            "industry": industry_allocation,
            "stock": stock_allocation
        }
