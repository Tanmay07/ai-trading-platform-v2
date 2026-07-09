import pandas as pd
import logging
from typing import Optional, List

from data_platform.storage.parquet_manager import ParquetManager
from ml_platform.feature_store.feature_cache import FeatureCache
from ml_platform.feature_store.feature_registry import FeatureRegistry

from ml_platform.feature_engineering.technical_features import TechnicalFeatures
from ml_platform.feature_engineering.volatility_features import VolatilityFeatures
from ml_platform.feature_engineering.volume_features import VolumeFeatures
from ml_platform.feature_engineering.price_action_features import PriceActionFeatures

logger = logging.getLogger(__name__)

class FeatureStore:
    """
    Central interface for fetching and generating ML features.
    Reads from Historical Data Lake, generates features, caches them,
    and registers them in the FeatureRegistry.
    """
    
    def __init__(self):
        self.raw_data_manager = ParquetManager()
        self.cache = FeatureCache()
        self.registry = FeatureRegistry()
        
        self._initialize_registry()

    def _initialize_registry(self):
        # Register the features we know we generate
        self.registry.register_feature_group(
            "trend", ["EMA_10", "EMA_20", "EMA_50", "EMA_100", "EMA_200", "SMA_20", "SMA_50", "RSI_14", "MACD_Line", "MACD_Signal", "MACD_Hist", "Dist_EMA_20", "Dist_EMA_50"], "1.0", "Trend indicators"
        )
        self.registry.register_feature_group(
            "volatility", ["ATR_14", "BB_Upper", "BB_Lower", "BB_Width", "BB_Pct_B", "Daily_Return", "Hist_Vol_20"], "1.0", "Volatility indicators"
        )
        self.registry.register_feature_group(
            "volume", ["Vol_SMA_20", "Rel_Volume", "OBV", "VWAP_14", "OBV_SMA_20"], "1.0", "Volume indicators"
        )
        self.registry.register_feature_group(
            "price_action", ["Gap_Pct", "Candle_Body", "Upper_Wick_Ratio", "Lower_Wick_Ratio", "Rolling_High_20", "Rolling_Low_20", "Dist_Res_20", "Dist_Sup_20"], "1.0", "Price action and SR"
        )

    def generate_features_for_symbol(self, symbol: str, force_recompute: bool = False) -> pd.DataFrame:
        """
        Generates all registered features for a symbol.
        Uses cached version if available and not forced to recompute.
        """
        if not force_recompute:
            cached_df = self.cache.load_features(symbol)
            if not cached_df.empty:
                logger.debug(f"Loaded features from cache for {symbol}")
                return cached_df
                
        # Load raw data
        raw_df = self.raw_data_manager.load_symbol_data(symbol)
        if raw_df.empty:
            logger.warning(f"No raw data found for {symbol} to generate features.")
            return pd.DataFrame()
            
        logger.info(f"Generating features for {symbol} ({len(raw_df)} rows)...")
        
        # Apply Feature Engineering pipelines
        df = raw_df.copy()
        
        df = TechnicalFeatures.add_trend_features(df)
        df = VolatilityFeatures.add_volatility_features(df)
        df = VolumeFeatures.add_volume_features(df)
        df = PriceActionFeatures.add_price_action_features(df)
        
        # Drop rows with NaNs caused by rolling windows (e.g. first 200 days for EMA_200)
        # In a real system, you might want to keep them or handle them differently.
        # We will forward fill what we can and drop the absolute beginning.
        df.ffill(inplace=True)
        df.dropna(inplace=True)
        
        # Save to cache
        self.cache.save_features(df, symbol)
        
        return df
        
    def get_features(self, symbol: str, start_date=None, end_date=None) -> pd.DataFrame:
        """Fetch features, bounded by optional dates."""
        df = self.generate_features_for_symbol(symbol)
        if df.empty:
            return df
            
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
            
        return df
