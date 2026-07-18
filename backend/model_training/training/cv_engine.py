import pandas as pd
import numpy as np
import logging
from typing import Generator, Tuple

logger = logging.getLogger("PurgedWalkForwardCV")

class PurgedWalkForwardCV:
    def __init__(self, n_splits: int = 3, embargo_pct: float = 0.02):
        """
        Custom Cross Validator for Financial Time Series.
        Prevents data leakage through chronological splitting and purging (embargo).
        
        Args:
            n_splits: Number of Walk-Forward folds.
            embargo_pct: Percentage of data to drop between train and val to prevent leakage 
                         (e.g., from forward returns overlapping).
        """
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct

    def split(self, df: pd.DataFrame) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Yields train and validation indices.
        Assumes df is chronologically sorted by 'Date' or has an implicit chronological order.
        """
        n_samples = len(df)
        indices = np.arange(n_samples)
        
        # We need (n_splits + 1) chunks
        chunk_size = n_samples // (self.n_splits + 1)
        embargo_size = int(n_samples * self.embargo_pct)
        
        for fold in range(self.n_splits):
            train_end = chunk_size * (fold + 1)
            
            # The validation set is the chunk right after the train set, but we apply an embargo gap
            val_start = train_end + embargo_size
            val_end = chunk_size * (fold + 2)
            
            if val_start >= val_end:
                val_start = train_end # fallback if embargo is too large
                
            train_indices = indices[0:train_end]
            val_indices = indices[val_start:val_end]
            
            yield train_indices, val_indices
