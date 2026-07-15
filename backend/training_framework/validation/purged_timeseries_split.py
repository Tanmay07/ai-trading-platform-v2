import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from typing import Generator, Tuple

from .embargo_split import apply_purge_and_embargo

class PurgedTimeSeriesSplit(TimeSeriesSplit):
    """
    Time Series cross-validator providing train/test indices to split time series data samples
    that are observed at fixed time intervals, in train/test sets.
    
    In each split, test indices must be higher than before, and thus shuffling in cross validator is inappropriate.
    
    Applies Purge (removes overlapping prediction horizon) and Embargo (removes data post-test set) 
    to the training indices to prevent look-ahead bias and autocorrelation leakage.
    """
    def __init__(self, n_splits=5, max_train_size=None, test_size=None, gap=0, 
                 prediction_horizon_days=5, embargo_days=7):
        super().__init__(n_splits=n_splits, max_train_size=max_train_size, test_size=test_size, gap=gap)
        self.prediction_horizon_days = prediction_horizon_days
        self.embargo_days = embargo_days
        
    def split(self, X, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Generate indices to split data into training and test set.
        """
        # Ensure X has a datetime index for date math
        if not hasattr(X, 'index'):
            raise ValueError("X must be a pandas DataFrame with a DatetimeIndex or a MultiIndex containing Date.")
            
        if isinstance(X.index, pd.MultiIndex):
            if 'Date' in X.index.names:
                dates = pd.Series(X.index.get_level_values('Date'))
            else:
                raise ValueError("MultiIndex must contain 'Date' level.")
        else:
            dates = pd.Series(X.index)
            
        if not pd.api.types.is_datetime64_any_dtype(dates):
             dates = pd.to_datetime(dates)
             
        for train_indices, test_indices in super().split(X, y, groups):
            # Apply purge and embargo
            purged_train_indices = apply_purge_and_embargo(
                dates, 
                train_indices, 
                test_indices, 
                prediction_horizon_days=self.prediction_horizon_days, 
                embargo_days=self.embargo_days
            )
            
            print(f"DEBUG: CV Fold Yield -> Train: {len(purged_train_indices)}, Test: {len(test_indices)}")
            yield purged_train_indices, test_indices
