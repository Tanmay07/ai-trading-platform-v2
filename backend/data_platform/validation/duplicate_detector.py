import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """Detects and handles duplicate records in time series data."""

    @staticmethod
    def remove_duplicates(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Removes exact duplicate rows based on the Datetime index.
        Keeps the last occurrence.
        """
        if df.empty:
            return df
            
        initial_len = len(df)
        # Drop rows with identical index
        df_clean = df[~df.index.duplicated(keep='last')]
        
        duplicates_removed = initial_len - len(df_clean)
        if duplicates_removed > 0:
            logger.info(f"{symbol}: Removed {duplicates_removed} duplicate dates.")
            
        return df_clean
