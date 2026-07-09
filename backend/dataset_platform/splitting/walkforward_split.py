import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger("WalkforwardSplit")

class WalkforwardSplitter:
    """
    Time-Series Cross Validation (Walk-forward).
    Prevents leakage by ensuring Train strictly precedes Validation, and Validation strictly precedes Test.
    """
    def __init__(self, train_years: int = 3, val_years: int = 1, test_years: int = 1):
        self.train_years = train_years
        self.val_years = val_years
        self.test_years = test_years
        
    def generate_splits(self, df: pd.DataFrame) -> List[Dict[str, pd.DataFrame]]:
        """
        Takes a multi-year dataframe and returns a list of dictionaries containing Train/Val/Test dataframes.
        Each dictionary is one "fold" or "window" of the walk-forward evaluation.
        """
        if df.empty or not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must be non-empty and have a DatetimeIndex.")
            
        splits = []
        min_date = df.index.min()
        max_date = df.index.max()
        
        current_start = min_date
        
        while True:
            train_end = current_start + pd.DateOffset(years=self.train_years)
            val_end = train_end + pd.DateOffset(years=self.val_years)
            test_end = val_end + pd.DateOffset(years=self.test_years)
            
            if test_end > max_date:
                break
                
            train_df = df[(df.index >= current_start) & (df.index < train_end)]
            val_df = df[(df.index >= train_end) & (df.index < val_end)]
            test_df = df[(df.index >= val_end) & (df.index < test_end)]
            
            splits.append({
                "train": train_df,
                "val": val_df,
                "test": test_df,
                "window": f"{current_start.date()} to {test_end.date()}"
            })
            
            # Slide the window forward by the test period
            current_start += pd.DateOffset(years=self.test_years)
            
        logger.info(f"Generated {len(splits)} walk-forward splits.")
        return splits
