import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ApiUsageMonitor:
    """Tracks API usage across providers to prevent rate limiting."""
    
    def __init__(self):
        self.stats = {
            "yahoo_calls": 0,
            "jugaad_calls": 0,
            "nse_calls": 0,
            "failures": 0,
            "retries": 0
        }
        
    def log_call(self, provider: str, success: bool = True):
        key = f"{provider.lower()}_calls"
        if key in self.stats:
            self.stats[key] += 1
            
        if not success:
            self.stats["failures"] += 1
            
    def log_retry(self):
        self.stats["retries"] += 1
        
    def get_usage(self) -> Dict[str, Any]:
        return self.stats.copy()
