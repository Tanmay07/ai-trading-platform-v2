from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date
from market_data.models.dto import MarketQuote, HistoricalCandle, CorporateAction, MarketStatus, IndexData

class MarketDataProvider(ABC):
    """Exhaustive Provider Interface for Market Data."""
    
    def get_live_quote(self, symbol: str) -> MarketQuote:
        raise NotImplementedError()
        
    def get_live_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        raise NotImplementedError()
        
    def get_historical_data(self, symbol: str, start_date: date, end_date: date) -> List[HistoricalCandle]:
        raise NotImplementedError()
        
    def get_intraday_data(self, symbol: str) -> List[HistoricalCandle]:
        raise NotImplementedError()
        
    def get_indices(self) -> List[IndexData]:
        raise NotImplementedError()
        
    def get_index(self, index_name: str) -> IndexData:
        raise NotImplementedError()
        
    def get_market_status(self) -> MarketStatus:
        raise NotImplementedError()
        
    def get_trading_calendar(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()
        
    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        raise NotImplementedError()
        
    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        raise NotImplementedError()
        
    def get_symbol_master(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_provider_name(self) -> str:
        pass

BaseIntradayProvider = MarketDataProvider
