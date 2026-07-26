import pytest
from datetime import datetime
from market_data.service import MarketDataService
from market_data.providers.base_provider import MarketDataProvider
from market_data.models.dto import MarketQuote

class MockProvider(MarketDataProvider):
    def get_live_quote(self, symbol: str) -> MarketQuote:
        return MarketQuote(
            symbol=symbol,
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            previous_close=100.0,
            last_price=102.0,
            volume=1000,
            validation_score=100
        )
    def get_live_quotes(self, symbols): return {}
    def get_historical_data(self, symbol, start, end): return []
    def get_intraday_data(self, symbol): return []
    def get_indices(self): return []
    def get_index(self, name): return None
    def get_market_status(self): return None
    def get_trading_calendar(self): return []
    def get_corporate_actions(self, symbol): return []
    def search_symbol(self, query): return []
    def get_symbol_master(self): return []
    def get_provider_name(self): return "mock"

def test_market_data_service():
    service = MarketDataService(provider=MockProvider())
    quote = service.get_live_quote("TEST")
    
    assert quote.symbol == "TEST"
    assert quote.last_price == 102.0
    assert quote.volume == 1000
    
    # Check cache hit
    cached_quote = service.get_live_quote("TEST")
    assert cached_quote is quote
