import redis
import json
import logging
from typing import Any, Optional
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Interfaces with Redis. 
    Gracefully falls back to an in-memory dictionary if Redis is unreachable.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("market_data")
        redis_url = self.config.get("redis", {}).get("url", "redis://localhost:6379/0")
        self.fallback = self.config.get("redis", {}).get("fallback_to_memory", True)
        
        self.r = None
        self._memory_cache = {} # Fallback
        self._memory_ttl = {}
        
        try:
            self.r = redis.from_url(redis_url, decode_responses=True)
            self.r.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            if self.fallback:
                logger.warning(f"Redis connection failed. Falling back to in-memory cache. ({e})")
                self.r = None
            else:
                raise Exception(f"Redis is required but unreachable: {e}")
                
    def set(self, key: str, value: Any, ttl_seconds: int = 900) -> bool:
        try:
            val_str = json.dumps(value)
            if self.r:
                return self.r.setex(key, ttl_seconds, val_str)
            else:
                import time
                self._memory_cache[key] = val_str
                self._memory_ttl[key] = time.time() + ttl_seconds
                return True
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        try:
            if self.r:
                val_str = self.r.get(key)
                return json.loads(val_str) if val_str else None
            else:
                import time
                if key in self._memory_cache:
                    if time.time() > self._memory_ttl.get(key, 0):
                        del self._memory_cache[key]
                        del self._memory_ttl[key]
                        return None
                    return json.loads(self._memory_cache[key])
                return None
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None
            
    def delete(self, key: str) -> bool:
        try:
            if self.r:
                return bool(self.r.delete(key))
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    del self._memory_ttl[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False
