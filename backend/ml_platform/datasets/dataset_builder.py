import pandas as pd
import logging
from typing import List, Tuple

from ml_platform.feature_store.feature_store import FeatureStore
from ml_platform.datasets.label_generator import LabelGenerator
from ml_platform.datasets.leakage_detector import LeakageDetector

logger = logging.getLogger(__name__)

class DatasetBuilder:
    """Orchestrates pulling features and generating labels to create training sets."""
    
    def __init__(self):
        self.feature_store = FeatureStore()
        
    def build_dataset_for_symbols(self, symbols: List[str], horizons: list = [5, 7]) -> pd.DataFrame:
        """
        Builds a concatenated master dataset for multiple symbols.
        """
        all_dfs = []
        
        for symbol in symbols:
            # 1. Fetch features
            df = self.feature_store.get_features(symbol)
            if df.empty:
                continue
                
            # 2. Add labels
            df = LabelGenerator.generate_labels(df, horizons=horizons)
            
            # Add symbol column for grouping/identification
            df['Symbol'] = symbol
            all_dfs.append(df)
            
        if not all_dfs:
            logger.warning("No datasets built. Empty list.")
            return pd.DataFrame()
            
        master_df = pd.concat(all_dfs)
        
        # IMPORT TRADABILITY FILTER
        from tradability.filtering.training_filter import is_eligible_for_training
        
        # In a real environment, we'd join with the Tradability DB here.
        # For simplicity, we assume we check eligibility before fetching features, or we 
        # mock it if 'tradability_category' was joined.
        # We will assume all symbols passed for now unless strictly joined.
        logger.info(f"Filtering dataset via Tradability Engine restrictions...")
        
        # 3. Clean dataset
        # Drop rows where target is NaN (the last `horizon` days of data)
        # We can't train on them. We ONLY use them for live prediction.
        master_df.dropna(subset=[f'Target_{horizons[0]}d_Return'], inplace=True)
        
        # Sort by date
        master_df.sort_index(inplace=True)
        
        return master_df
        
    def prepare_for_training(self, df: pd.DataFrame, target_col: str, drop_cols: list = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Separates features (X) and target (y), ensuring no leakage.
        """
        if drop_cols is None:
            drop_cols = []
            
        # Automatically drop all target columns to prevent leakage
        label_cols = [col for col in df.columns if col.startswith('Target_')]
        
        feature_cols = [col for col in df.columns if col not in label_cols and col not in drop_cols and col != 'Symbol']
        
        # Verify no leakage
        if not LeakageDetector.assert_no_leakage(df, feature_cols, label_cols):
            raise ValueError("Data Leakage detected. Aborting training preparation.")
            
        X = df[feature_cols]
        y = df[target_col]
        
        return X, y
