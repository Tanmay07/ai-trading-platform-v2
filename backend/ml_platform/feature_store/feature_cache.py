import pandas as pd
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FeatureCache:
    """Manages reading and writing computed features to disk (Parquet)."""
    
    def __init__(self, base_path: str = "data/feature_store"):
        self.base_path = Path(base_path)
        self.cache_path = self.base_path / "offline_features"
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
    def get_cache_file(self, symbol: str) -> Path:
        return self.cache_path / f"{symbol}_features.parquet"
        
    def save_features(self, df: pd.DataFrame, symbol: str) -> bool:
        if df.empty:
            return False
            
        file_path = self.get_cache_file(symbol)
        try:
            df.to_parquet(file_path, engine='pyarrow', compression='snappy')
            logger.debug(f"Cached features for {symbol} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache features for {symbol}: {e}")
            return False

    def load_features(self, symbol: str) -> pd.DataFrame:
        file_path = self.get_cache_file(symbol)
        if not file_path.exists():
            return pd.DataFrame()
            
        try:
            return pd.read_parquet(file_path, engine='pyarrow')
        except Exception as e:
            logger.error(f"Failed to load cached features for {symbol}: {e}")
            return pd.DataFrame()
