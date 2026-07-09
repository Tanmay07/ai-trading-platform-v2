from typing import Dict, Any
from app.config_portfolio import portfolio_config

class CorrelationEngine:
    def calculate_correlation_impact(self, current_portfolio: Dict[str, Any], candidate_ticker: str) -> float:
        """
        Calculates how correlated the new candidate is to the existing portfolio.
        Returns a float between -1.0 and 1.0.
        """
        # In a real system, we'd fetch yfinance timeseries and do df.corr()
        # For MVP, we mock a mild positive correlation
        return 0.25

    def is_acceptable(self, correlation: float) -> bool:
        return correlation < portfolio_config.limits.correlation_threshold
