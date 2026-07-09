import logging
from data_platform.universe.universe_manager import UniverseManager
from data_platform.providers.yahoo_provider import YahooProvider
from feature_platform.engine.incremental_engine import IncrementalEngine
from feature_platform.storage.feature_store import FeatureStore
from datetime import datetime

logger = logging.getLogger("FeaturePipeline")

class FeaturePipeline:
    def __init__(self):
        self.incremental = IncrementalEngine()
        self.store = FeatureStore()
        self.universe = UniverseManager()
        self.provider = YahooProvider()
        
    async def run_pipeline(self, symbol: str):
        """
        End-to-End flow for a single symbol:
        1. Check Feature Store for last updated date.
        2. Fetch raw OHLCV from Historical Data Platform.
        3. Run Incremental Engine.
        4. Append to Feature Store.
        """
        try:
            last_date = self.store.get_last_updated_date(symbol)
            # Use a robust start_date for 10 years back
            start_date = datetime(datetime.now().year - 10, datetime.now().month, datetime.now().day)
            raw_df = self.provider.get_symbol_history(symbol, start_date=start_date, end_date=datetime.now())
            
            if raw_df.empty:
                return
                
            if last_date:
                new_features = self.incremental.process_incremental_update(raw_df, last_date)
                if not new_features.empty:
                    self.store.append_features(symbol, new_features)
            else:
                # Full historical backfill
                engine = self.incremental.feature_engine
                full_features = engine.generate_features_for_df(raw_df)
                self.store.save_features(symbol, full_features)
                
            logger.info(f"[{symbol}] Feature Pipeline completed.")
            
        except Exception as e:
            logger.error(f"[{symbol}] Pipeline failed: {e}")
