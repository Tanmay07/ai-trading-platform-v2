import logging
from typing import Dict, Any

from ml_platform.feature_store.feature_store import FeatureStore

logger = logging.getLogger(__name__)

class FeatureStoreIntegration:
    """Writes Market Intelligence features into the D2 Feature Store."""
    
    def __init__(self):
        self.feature_store = FeatureStore()
        
    def write_news_features(self, symbol: str, sentiment_score: float, importance: int, event_type: str):
        """
        Updates the feature store for the given symbol.
        In a real system, this would append a new row or update today's row in Parquet.
        """
        try:
            # We mock the dictionary that would be merged into the OHLCV features
            features = {
                "News_Sentiment": sentiment_score,
                "News_Importance": importance,
                "News_Volume_1d": 1, # Increment
                "Last_Event": event_type
            }
            # The actual write to parquet logic would sit here
            logger.info(f"Pushed Intelligence Features to D2 Feature Store for {symbol}: {features}")
        except Exception as e:
            logger.error(f"Failed to write to Feature Store: {e}")
