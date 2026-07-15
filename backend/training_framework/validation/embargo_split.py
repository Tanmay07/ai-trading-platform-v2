import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("EmbargoSplit")

def apply_purge_and_embargo(
    dates: pd.Series, 
    train_indices: np.ndarray, 
    test_indices: np.ndarray, 
    prediction_horizon_days: int = 5,
    embargo_days: int = 7
) -> np.ndarray:
    """
    Applies Purge (removes overlapping prediction horizon) and 
    Embargo (removes data post-test set) to the training indices.
    
    Returns the filtered train_indices.
    """
    if len(test_indices) == 0:
        return train_indices
        
    test_start = dates.iloc[test_indices].min()
    test_end = dates.iloc[test_indices].max()
    
    # Purge: Training data before test data cannot overlap with test data prediction horizon
    # So max train date < test_start - prediction_horizon_days
    purge_cutoff = test_start - pd.Timedelta(days=prediction_horizon_days)
    
    # Embargo: Training data after test data cannot be immediately after (prevent autocorrelation leakage)
    # So min train date > test_end + embargo_days
    embargo_cutoff = test_end + pd.Timedelta(days=embargo_days)
    
    # Filter train indices
    train_dates = dates.iloc[train_indices]
    
    valid_mask = (train_dates < purge_cutoff) | (train_dates > embargo_cutoff)
    
    purged_embargoed_train = train_indices[valid_mask]
    
    dropped = len(train_indices) - len(purged_embargoed_train)
    if dropped > 0:
        logger.debug(f"Purged/Embargoed {dropped} overlapping training samples.")
        
    return purged_embargoed_train
