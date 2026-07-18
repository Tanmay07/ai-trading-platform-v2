import abc
from typing import List, Dict, Any

class PortfolioConstraint(abc.ABC):
    """
    Base class for all portfolio optimization constraints.
    """
    @abc.abstractmethod
    def check_candidate(self, candidate: Dict[str, Any], current_portfolio: List[Dict[str, Any]]) -> bool:
        """
        Returns True if the candidate CAN be added to the portfolio, False if it violates the constraint.
        """
        pass
        
    @abc.abstractmethod
    def get_rejection_reason(self) -> str:
        pass


class MaxPositionsConstraint(PortfolioConstraint):
    def __init__(self, max_positions: int):
        self.max_positions = max_positions
        
    def check_candidate(self, candidate: Dict[str, Any], current_portfolio: List[Dict[str, Any]]) -> bool:
        return len(current_portfolio) < self.max_positions
        
    def get_rejection_reason(self) -> str:
        return f"Portfolio has reached maximum positions ({self.max_positions})"


class MaxSectorExposureConstraint(PortfolioConstraint):
    def __init__(self, max_exposure: float):
        self.max_exposure = max_exposure
        
    def check_candidate(self, candidate: Dict[str, Any], current_portfolio: List[Dict[str, Any]]) -> bool:
        sector = candidate.get('sector', 'Unknown')
        
        # Count current members in this sector
        current_sector_count = sum(1 for c in current_portfolio if c.get('sector', 'Unknown') == sector)
        
        # Estimate new exposure (assuming roughly equal weight for the check, or just max positions ratio)
        # For a stricter check during allocation we'd use capital, but for selection we use count / max_expected_positions
        # Here we just use a naive count ratio against an assumed typical portfolio size (e.g. 10)
        # A more robust check requires knowing the target portfolio size. 
        # For now, let's limit the absolute count based on max_exposure * 15 (max positions config default)
        max_allowed_count = max(1, int(self.max_exposure * 15))
        
        return current_sector_count < max_allowed_count
        
    def get_rejection_reason(self) -> str:
        return f"Sector exposure limit ({self.max_exposure*100}%) reached"


class CorrelationConstraint(PortfolioConstraint):
    def __init__(self, threshold: float, correlation_engine):
        self.threshold = threshold
        self.engine = correlation_engine
        
    def check_candidate(self, candidate: Dict[str, Any], current_portfolio: List[Dict[str, Any]]) -> bool:
        symbol = candidate['symbol']
        for existing in current_portfolio:
            corr = self.engine.get_correlation(symbol, existing['symbol'])
            if corr > self.threshold:
                self.last_violator = existing['symbol']
                return False
        return True
        
    def get_rejection_reason(self) -> str:
        return f"Highly correlated (>{self.threshold}) with existing position {getattr(self, 'last_violator', 'Unknown')}"
