import pandas as pd
import logging
from alpha_registry.optimization.alpha_selector import AlphaSelector
from feature_platform.storage.feature_store import FeatureStore
from data_platform.providers.yahoo_provider import YahooProvider
from datetime import datetime

logger = logging.getLogger("FeatureJoiner")

class FeatureJoiner:
    """
    Safely joins Historical Data, Alpha Factors, and Tradability Scores.
    """
    def __init__(self):
        self.alpha_selector = AlphaSelector()
        self.feature_store = FeatureStore()
        self.provider = YahooProvider()
        
    async def build_symbol_dataframe(self, symbol: str) -> pd.DataFrame:
        """
        Fetches all required data for a single symbol and joins them on the DatetimeIndex.
        """
        # 1. Fetch raw OHLCV
        try:
            start_date = datetime(datetime.now().year - 10, datetime.now().month, datetime.now().day)
            ohlcv_df = self.provider.get_symbol_history(symbol, start_date=start_date, end_date=datetime.now())
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV for {symbol}: {e}")
            return pd.DataFrame()
            
        if ohlcv_df.empty:
            return pd.DataFrame()
            
        # 2. Fetch Alpha Features
        try:
            # We bypass the legacy ML Feature Store and go straight to the E2 Feature Store
            import os
            path = self.feature_store._get_path(symbol)
            if not os.path.exists(path):
                logger.warning(f"No alpha features found for {symbol}")
                return pd.DataFrame()
                
            alpha_df = pd.read_parquet(path)
        except Exception as e:
            logger.error(f"Failed to fetch Alphas for {symbol}: {e}")
            return pd.DataFrame()
            
        # 3. Filter only approved Alpha Factors
        approved_alphas = self.alpha_selector.get_production_features()
        available_alphas = [col for col in alpha_df.columns if col in approved_alphas]
        filtered_alpha_df = alpha_df[available_alphas]
        
        # 4. Join exactly on Index (Date)
        # Use inner join so we only keep days where we have both OHLCV and Features
        merged_df = ohlcv_df.join(filtered_alpha_df, how='inner')
        
        # 5. Add Symbol
        merged_df['Symbol'] = symbol
        
        return merged_df
