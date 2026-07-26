from typing import List, Dict
from portfolio_manager.schemas import HoldingResponse
from datetime import datetime

class PerformanceAnalytics:
    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, days_elapsed: int) -> float:
        if start_value <= 0 or days_elapsed <= 0:
            return 0.0
        years = days_elapsed / 365.25
        if years == 0:
            return 0.0
        cagr = ( (end_value / start_value) ** (1 / years) ) - 1
        return cagr * 100

    @staticmethod
    def calculate_xirr(cash_flows: List[tuple], guess: float = 0.1) -> float:
        """
        Placeholder for XIRR calculation.
        cash_flows: List of (date, amount) where amount is negative for investments, positive for withdrawals/current value.
        """
        # Complex calculation typically requiring scipy or iterative approach.
        return 0.0 

    @staticmethod
    def get_portfolio_performance(holdings: List[HoldingResponse], base_capital: float, start_date: datetime) -> Dict[str, float]:
        total_invested = sum(h.total_invested for h in holdings)
        total_value = sum(h.current_value for h in holdings) if holdings else 0.0
        
        days_elapsed = max((datetime.utcnow() - start_date).days, 1) if start_date else 1
        cagr = PerformanceAnalytics.calculate_cagr(total_invested, total_value, days_elapsed)

        return {
            "total_value": total_value,
            "total_invested": total_invested,
            "absolute_return": total_value - total_invested,
            "absolute_return_pct": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "cagr": cagr,
            "daily_return": 0.0 # Requires historical snapshots to calculate properly
        }
