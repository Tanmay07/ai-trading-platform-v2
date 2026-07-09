from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseIntradayProvider(ABC):
    """Base interface for fetching real-time and intraday market data."""
    
    @abstractmethod
    def fetch_current_price(self, symbol: str) -> Dict[str, Any]:
        """Fetches the latest snapshot (OHLCV) for a symbol."""
        pass
        
    @abstractmethod
    def fetch_batch_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetches latest snapshot for multiple symbols."""
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
