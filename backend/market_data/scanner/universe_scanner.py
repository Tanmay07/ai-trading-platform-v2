import logging
from typing import List, Dict, Any

from market_data.orchestrator.market_data_orchestrator import MarketDataOrchestrator
from market_data.scanner.smart_filter import SmartFilter
from ml_platform.feature_store.feature_store import FeatureStore
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class UniverseScanner:
    """Rapidly scans the entire universe to populate the Candidate Queue."""
    
    def __init__(self, orchestrator: MarketDataOrchestrator, config_manager: ConfigManager):
        self.orchestrator = orchestrator
        self.smart_filter = SmartFilter(config_manager)
        self.feature_store = FeatureStore()
        
    def run_scan(self, universe: List[str]):
        """Runs a lightweight scan over the universe."""
        logger.info(f"Starting Universe Scan for {len(universe)} symbols...")
        
        # 1. Fetch live batch (Orchestrator handles cache vs API)
        # We don't force refresh here, we just take what Orchestrator has
        live_data = self.orchestrator.get_batch_prices(universe, force_refresh=False)
        
        candidates_found = 0
        for symbol, data in live_data.items():
            if data.get("status") != "success":
                continue
                
            # 2. Get historical context from ML platform (D2)
            hist_df = self.feature_store.get_features(symbol)
            if hist_df.empty:
                continue
            
            # Get yesterday's features
            hist_context = hist_df.iloc[-1].to_dict()
            
            # 3. Filter
            passed = self.smart_filter.evaluate(symbol, data, hist_context)
            if passed:
                candidates_found += 1
                
        # 4. Trigger events for priorities
        # EventTriggerEngine is already called during forced refreshes, 
        # but we could also call it here if desired.
        
        logger.info(f"Scan complete. {candidates_found} candidates found.")
        logger.info(f"Current Queue Size: {len(self.smart_filter.get_candidates())}")
        
    def get_candidate_queue(self) -> List[str]:
        return self.smart_filter.get_candidates()
