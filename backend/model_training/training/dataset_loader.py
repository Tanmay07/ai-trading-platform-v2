import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger("DatasetLoader")

class DatasetLoader:
    def __init__(self, data_path: str = "data/ml_datasets/dataset_v1.parquet"):
        self.data_path = Path(data_path)
        
    def load_dataset(self) -> pd.DataFrame:
        """Loads the complete generated dataset."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        logger.info(f"Loading dataset from {self.data_path}")
        df = pd.read_parquet(self.data_path)
        return df

    def perform_feature_selection(self, df: pd.DataFrame, drop_cols: list = None) -> pd.DataFrame:
        """
        Removes constants, duplicates, >0.95 correlated, and excessive NaNs.
        Returns the cleaned feature dataframe.
        """
        logger.info(f"Starting feature selection on {df.shape[1]} columns...")
        
        # Base drops
        if drop_cols:
            df = df.drop(columns=drop_cols, errors='ignore')
            
        # 1. Drop excessive NaNs (>30% missing)
        missing_ratios = df.isna().mean()
        to_drop_nan = missing_ratios[missing_ratios > 0.3].index.tolist()
        df.drop(columns=to_drop_nan, inplace=True)
        logger.info(f"Dropped {len(to_drop_nan)} columns due to excessive NaNs.")

        # 2. Drop Constants
        constants = [col for col in df.columns if df[col].nunique() <= 1]
        df.drop(columns=constants, inplace=True)
        logger.info(f"Dropped {len(constants)} constant columns.")
        
        # 3. Correlation filter (Highly correlated > 0.95)
        # Calculate correlation only on numeric columns
        corr_matrix = df.select_dtypes(include=[np.number]).corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop_corr = [column for column in upper.columns if any(upper[column] > 0.95)]
        df.drop(columns=to_drop_corr, inplace=True)
        logger.info(f"Dropped {len(to_drop_corr)} columns due to >0.95 correlation.")
        
        logger.info(f"Feature selection complete. Retained {df.shape[1]} columns.")
        return df

    def split_time_series(self, df: pd.DataFrame, target_col: str):
        """
        Splits data based on date ranges:
        Train: <= 2022
        Val: 2023
        Test: >= 2024
        """
        # Ensure we have a DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            # If MultiIndex (Date, Symbol), unstack or check level
            if 'Date' in df.index.names:
                dates = df.index.get_level_values('Date')
            else:
                raise ValueError("Dataset must have 'Date' in index for time-series split.")
        else:
            dates = df.index
            
        train_mask = dates.year <= 2022
        val_mask = dates.year == 2023
        test_mask = dates.year >= 2024
        
        # Features and target
        X = df.drop(columns=[target_col], errors='ignore')
        y = df[target_col]
        
        X_train, y_train = X[train_mask], y[train_mask]
        X_val, y_val = X[val_mask], y[val_mask]
        X_test, y_test = X[test_mask], y[test_mask]
        
        logger.info(f"Train split: {X_train.shape[0]} samples")
        logger.info(f"Val split: {X_val.shape[0]} samples")
        logger.info(f"Test split: {X_test.shape[0]} samples")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
