import os
import pandas as pd
from datetime import datetime
import logging
import yaml

logger = logging.getLogger("FeatureStore")

class FeatureStore:
    """
    Abstraction layer for reading/writing feature DataFrames to Parquet.
    """
    def __init__(self):
        with open("config/feature_store.yaml", "r") as f:
            self.config = yaml.safe_load(f)["feature_store"]
        self.parquet_dir = self.config["parquet_dir"]
        os.makedirs(self.parquet_dir, exist_ok=True)
        
    def _get_path(self, symbol: str) -> str:
        return os.path.join(self.parquet_dir, f"{symbol}_features.parquet")
        
    def get_last_updated_date(self, symbol: str) -> datetime:
        path = self._get_path(symbol)
        if not os.path.exists(path):
            return None
            
        try:
            # Just read the last row to get the index (date)
            # In a real big data env we'd use pyarrow parquet metadata or a DB pointer
            df = pd.read_parquet(path)
            if df.empty:
                return None
            return df.index.max()
        except Exception as e:
            logger.error(f"Failed to read parquet for {symbol}: {e}")
            return None
            
    def save_features(self, symbol: str, df: pd.DataFrame):
        path = self._get_path(symbol)
        df.to_parquet(path)
        
    def append_features(self, symbol: str, new_df: pd.DataFrame):
        path = self._get_path(symbol)
        if not os.path.exists(path):
            self.save_features(symbol, new_df)
            return
            
        existing_df = pd.read_parquet(path)
        combined = pd.concat([existing_df, new_df])
        # Drop duplicates just in case incremental logic overlapped
        combined = combined[~combined.index.duplicated(keep='last')]
        combined.sort_index(inplace=True)
        self.save_features(symbol, combined)
