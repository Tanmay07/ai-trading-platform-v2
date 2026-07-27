import logging
from typing import Dict, Any, List, Optional
from datetime import date

from market_data.providers.base_provider import MarketDataProvider
from market_data.providers.jugaad_provider import JugaadProvider
from market_data.cache.smart_cache import SmartCache
from market_data.validation.validator import DataValidator
from market_data.models.dto import MarketQuote, HistoricalCandle, MarketStatus
from market_data.exceptions import ProviderTimeoutError

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    The Single Source of Truth for Market Data.
    Every other component must consume data through this gateway.
    """
    
    def __init__(self, providers: Optional[List[MarketDataProvider]] = None):
        if providers:
            self.providers = providers
        else:
            self.providers = [JugaadProvider()]
            
        self.cache = SmartCache()
        self.validator = DataValidator()
        
    def get_live_quote(self, symbol: str) -> MarketQuote:
        """Fetches a live quote, utilizing cache, validation, and fallback providers."""
        cached = self.cache.get_quote(symbol)
        if cached:
            return cached
            
        last_error = None
        for provider in self.providers:
            try:
                quote = provider.get_live_quote(symbol)
                validated_quote = self.validator.validate_quote(quote)
                self.cache.set_quote(symbol, validated_quote)
                return validated_quote
            except Exception as e:
                logger.warning(f"Provider {provider.get_provider_name()} failed for {symbol}: {e}")
                last_error = e
                
        logger.error(f"All providers failed to fetch live quote for {symbol}. Last error: {last_error}")
        raise last_error or Exception(f"No providers available to fetch {symbol}")

    def get_live_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Fetches multiple quotes optimally with fallback."""
        results = {}
        missing = []
        
        for sym in symbols:
            cached = self.cache.get_quote(sym)
            if cached:
                results[sym] = cached
            else:
                missing.append(sym)
                
        if missing:
            logger.info(f"Fetching batch quotes for {len(missing)} symbols.")
            
            for provider in self.providers:
                if not missing:
                    break
                    
                try:
                    provider_results = provider.get_live_quotes(missing)
                    new_missing = []
                    
                    for sym in missing:
                        if sym in provider_results:
                            try:
                                validated = self.validator.validate_quote(provider_results[sym])
                                self.cache.set_quote(sym, validated)
                                results[sym] = validated
                            except Exception as e:
                                logger.warning(f"Validation failed for batch quote {sym} via {provider.get_provider_name()}: {e}")
                                new_missing.append(sym)
                        else:
                            new_missing.append(sym)
                            
                    missing = new_missing
                except Exception as e:
                    logger.warning(f"Batch fetch failed via {provider.get_provider_name()}: {e}")
                    
            if missing:
                logger.error(f"Failed to fetch quotes for symbols after trying all providers: {missing}")
                    
        return results

    def get_historical_data(self, symbol: str, start_date: date, end_date: date) -> List[HistoricalCandle]:
        """Fetches historical data, caching permanently if fully historical."""
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        cached = self.cache.get_historical(symbol, start_str, end_str)
        if cached:
            return cached
            
        data = self.provider.get_historical_data(symbol, start_date, end_date)
        self.cache.set_historical(symbol, start_str, end_str, data)
        return data

    def get_market_status(self) -> MarketStatus:
        from market_data.status.engine import MarketStatusEngine
        engine = MarketStatusEngine(self.provider)
        return engine.get_current_status()
