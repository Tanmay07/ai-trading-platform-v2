import time
from typing import Dict, Any, Optional
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

class SmartCache:
    """Intelligent TTL-aware cache for market data."""
    
    def __init__(self):
        # Cache live quotes for 60 seconds
        self.quotes_cache = TTLCache(maxsize=10000, ttl=60)
        # Cache historical data for 24 hours (86400 seconds)
        self.historical_cache = TTLCache(maxsize=1000, ttl=86400)
        # Cache indices for 60 seconds
        self.index_cache = TTLCache(maxsize=100, ttl=60)
        
    def get_quote(self, symbol: str) -> Optional[Any]:
        return self.quotes_cache.get(symbol)
        
    def set_quote(self, symbol: str, quote: Any):
        self.quotes_cache[symbol] = quote
        
    def get_historical(self, symbol: str, start: str, end: str) -> Optional[Any]:
        key = f"{symbol}_{start}_{end}"
        return self.historical_cache.get(key)
        
    def set_historical(self, symbol: str, start: str, end: str, data: Any):
        key = f"{symbol}_{start}_{end}"
        self.historical_cache[key] = data
        
    def clear_cache(self):
        self.quotes_cache.clear()
        self.historical_cache.clear()
        self.index_cache.clear()
        logger.info("Market data cache cleared manually.")
