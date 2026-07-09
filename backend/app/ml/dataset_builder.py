import pandas as pd
from typing import Tuple
from app.ml.feature_store import FeatureStore

class DatasetBuilder:
    def __init__(self):
        self.store = FeatureStore()
        
    def build_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Builds a structured (X, y) dataset, avoiding look-ahead bias.
        """
        df = self.store.fetch_training_data()
        
        if df.empty:
            return pd.DataFrame(), pd.Series()
            
        # Target column: target_hit (Binary Classification: 1=Hit Target, 0=Hit Stop/Expired)
        y = df['target_hit']
        
        # Drop metadata and targets from features
        cols_to_drop = ['ticker', 'timestamp', 'target_5d', 'target_hit', 'id', 'feature_data']
        cols_to_drop = [c for c in cols_to_drop if c in df.columns]
        X = df.drop(columns=cols_to_drop)
        
        # Basic imputation
        X = X.fillna(0)
        
        # Drop non-numeric for now to make ML simple
        X = X.select_dtypes(include=['number'])
        
        return X, y
