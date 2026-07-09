import json
from typing import Dict, Any, Optional

class RedisCache:
    def __init__(self):
        # MVP: In-memory fallback
        self.cache = {}
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        val = self.cache.get(key)
        return json.loads(val) if val else None
        
    def set(self, key: str, value: Dict[str, Any], expire_seconds: int = 3600):
        self.cache[key] = json.dumps(value)
        
    def invalidate(self, key: str):
        if key in self.cache:
            del self.cache[key]
