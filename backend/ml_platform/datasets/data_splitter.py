import pandas as pd
from typing import Tuple
from datetime import datetime

class DataSplitter:
    """Handles splitting time-series data without look-ahead bias."""
    
    @staticmethod
    def walk_forward_split(df: pd.DataFrame, train_months: int = 24, test_months: int = 6):
        """
        Yields (train_df, test_df) tuples for Walk-Forward Validation.
        """
        if df.empty:
            return
            
        start_date = df.index.min()
        end_date = df.index.max()
        
        current_train_start = start_date
        
        while True:
            train_end = current_train_start + pd.DateOffset(months=train_months)
            test_end = train_end + pd.DateOffset(months=test_months)
            
            if test_end > end_date:
                break
                
            train_df = df[(df.index >= current_train_start) & (df.index < train_end)]
            test_df = df[(df.index >= train_end) & (df.index < test_end)]
            
            yield train_df, test_df
            
            # Step forward by the test window size
            current_train_start += pd.DateOffset(months=test_months)
            
    @staticmethod
    def simple_time_split(df: pd.DataFrame, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Simple chronological split."""
        split_idx = int(len(df) * train_ratio)
        return df.iloc[:split_idx], df.iloc[split_idx:]
