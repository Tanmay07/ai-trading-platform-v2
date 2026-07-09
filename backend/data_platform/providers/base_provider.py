from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from datetime import datetime

class BaseProvider(ABC):
    """
    Abstract base class for all market data providers.
    All data returned must be standardized to a pandas DataFrame with:
    Index: datetime
    Columns: Open, High, Low, Close, Volume, Adj Close
    """

    @abstractmethod
    def get_symbol_history(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch historical OHLCV data for a specific date range."""
        pass

    @abstractmethod
    def get_latest_history(self, symbol: str, days: int = 5) -> pd.DataFrame:
        """Fetch the most recent N days of OHLCV data."""
        pass

    @abstractmethod
    def get_corporate_actions(self, symbol: str) -> pd.DataFrame:
        """Fetch historical corporate actions (splits, dividends)."""
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Check if the provider supports/recognizes this symbol."""
        pass

    @abstractmethod
    def provider_name(self) -> str:
        """Return the canonical name of this provider."""
        pass
