import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from market_data.orchestrator.priority_engine import PriorityEngine, PriorityLevel
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class RefreshPlanner:
    """Intelligently plans when to refresh stocks based on their priority."""
    
    def __init__(self, priority_engine: PriorityEngine, config_manager: ConfigManager):
        self.priority_engine = priority_engine
        self.config = config_manager.get_config("market_data")
        
        # Keep track of last refresh time per symbol
        self.last_refresh: Dict[str, datetime] = {}

    def needs_refresh(self, symbol: str) -> bool:
        """Determines if a symbol needs refreshing right now."""
        priority = self.priority_engine.get_priority(symbol)
        
        if priority == PriorityLevel.DORMANT:
            # End of day only
            # Let's mock a simple check. If we have no data, fetch once. 
            if symbol not in self.last_refresh:
                return True
            return False
            
        interval_secs = self.priority_engine.get_refresh_interval_seconds(priority)
        
        if symbol not in self.last_refresh:
            return True
            
        time_since = (datetime.now() - self.last_refresh[symbol]).total_seconds()
        return time_since >= interval_secs
        
    def mark_refreshed(self, symbol: str):
        self.last_refresh[symbol] = datetime.now()
        
    def get_refresh_queue(self, universe: List[str]) -> List[str]:
        """Returns a list of symbols that need refreshing right now."""
        queue = []
        for symbol in universe:
            if self.needs_refresh(symbol):
                queue.append(symbol)
        return queue
