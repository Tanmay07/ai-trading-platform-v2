import logging
from typing import List, Dict, Any
import asyncio

from data_platform.core.config_manager import ConfigManager
from market_data.providers.provider_router import ProviderRouter
from market_data.cache.cache_manager import CacheManager
from market_data.orchestrator.priority_engine import PriorityEngine
from market_data.orchestrator.event_trigger_engine import EventTriggerEngine
from market_data.orchestrator.refresh_planner import RefreshPlanner

logger = logging.getLogger(__name__)

class MarketDataOrchestrator:
    """
    The central brain of the Market Data Platform.
    Coordinates fetching, caching, and scheduling.
    No other service should hit providers directly.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.get_config("market_data")
        
        self.router = ProviderRouter(config_manager)
        self.cache = CacheManager(config_manager)
        
        self.priority_engine = PriorityEngine(config_manager)
        self.event_trigger_engine = EventTriggerEngine(self.priority_engine, config_manager)
        self.planner = RefreshPlanner(self.priority_engine, config_manager)
        
        self.batch_size = self.config.get("batching", {}).get("max_symbols_per_request", 50)
        
    def get_price(self, symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Gets a single price, preferring cache."""
        if not force_refresh:
            cached = self.cache.get_price(symbol)
            if cached:
                return cached
                
        # Cache miss or forced
        logger.debug(f"Fetching fresh data for {symbol}")
        result = self.router.get_price(symbol)
        
        if result.get("status") == "success":
            self.cache.set_price(symbol, result)
            self.planner.mark_refreshed(symbol)
            
            # TODO: Fire event trigger engine here if we have historical context
            # self.event_trigger_engine.process_tick(symbol, result['price'], result['volume'], context)
            
        return result

    def get_batch_prices(self, symbols: List[str], force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        results = {}
        missing = []
        
        # Check cache
        if not force_refresh:
            for sym in symbols:
                cached = self.cache.get_price(sym)
                if cached:
                    results[sym] = cached
                else:
                    missing.append(sym)
        else:
            missing = symbols
            
        if not missing:
            return results
            
        # Chunk requests
        for i in range(0, len(missing), self.batch_size):
            chunk = missing[i:i + self.batch_size]
            logger.info(f"Fetching batch of {len(chunk)} symbols...")
            fetched = self.router.get_batch_prices(chunk)
            
            for sym, data in fetched.items():
                if data.get("status") == "success":
                    self.cache.set_price(sym, data)
                    self.planner.mark_refreshed(sym)
                results[sym] = data
                
        return results
        
    def execute_refresh_cycle(self, universe: List[str]):
        """Called by a scheduler. Finds what needs refreshing and fetches it."""
        queue = self.planner.get_refresh_queue(universe)
        if not queue:
            logger.info("Refresh cycle: No symbols need refreshing right now.")
            return
            
        logger.info(f"Refresh cycle: Updating {len(queue)} symbols out of {len(universe)}...")
        self.get_batch_prices(queue, force_refresh=True)
