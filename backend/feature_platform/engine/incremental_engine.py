import logging
from feature_platform.engine.feature_engine import FeatureEngine
import pandas as pd
from datetime import datetime

logger = logging.getLogger("IncrementalEngine")

class IncrementalEngine:
    def __init__(self):
        self.feature_engine = FeatureEngine()
        
    def process_incremental_update(self, raw_historical_df: pd.DataFrame, last_processed_date: datetime) -> pd.DataFrame:
        """
        Given the full raw OHLCV DataFrame and a timestamp, isolates the new rows,
        prepends necessary lookback context to compute EMAs/RSIs correctly without NaNs,
        generates the features, and isolates just the new feature rows to append.
        """
        # Max lookback needed for our largest feature (e.g., 200 SMA)
        MAX_LOOKBACK = 250 
        
        if raw_historical_df.empty:
            return raw_historical_df
            
        raw_historical_df.sort_index(inplace=True)
        
        # Find index of last_processed_date
        past_df = raw_historical_df[raw_historical_df.index <= last_processed_date]
        new_df = raw_historical_df[raw_historical_df.index > last_processed_date]
        
        if new_df.empty:
            return pd.DataFrame()
            
        # Get lookback context
        lookback_df = past_df.tail(MAX_LOOKBACK)
        
        # Combine
        working_df = pd.concat([lookback_df, new_df])
        
        # Generate features
        featured_df = self.feature_engine.generate_features_for_df(working_df)
        
        # Isolate the new rows
        new_featured_df = featured_df[featured_df.index > last_processed_date]
        
        return new_featured_df
