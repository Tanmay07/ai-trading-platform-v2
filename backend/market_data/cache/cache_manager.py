import logging
from typing import Dict, Any, Optional
from market_data.cache.redis_cache import RedisCache
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class CacheManager:
    """Provides high-level methods to cache specific market data types."""
    
    def __init__(self, config_manager: ConfigManager):
        self.cache = RedisCache(config_manager)
        self.config = config_manager.get_config("market_data")
        self.ttls = self.config.get("cache_ttl", {})
        
        # Performance tracking
        self.hits = 0
        self.misses = 0

    def _get_ttl(self, data_type: str) -> int:
        return self.ttls.get(data_type, 900)
        
    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        key = f"price:{symbol}"
        data = self.cache.get(key)
        if data:
            self.hits += 1
        else:
            self.misses += 1
        return data
        
    def set_price(self, symbol: str, data: Dict[str, Any]):
        key = f"price:{symbol}"
        ttl = self._get_ttl("price")
        self.cache.set(key, data, ttl)

    def get_market_status(self) -> Optional[str]:
        data = self.cache.get("market:status")
        if data:
            self.hits += 1
        else:
            self.misses += 1
        return data
        
    def set_market_status(self, status: str):
        self.cache.set("market:status", status, self._get_ttl("market_status"))
        
    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(rate, 2)
        }
