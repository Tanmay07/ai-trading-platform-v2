import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Central validation orchestrator for OHLCV data.
    Runs multiple checks before data is allowed into the Data Lake.
    """
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame, symbol: str) -> bool:
        """
        Runs all validation checks on the DataFrame.
        Returns True if the dataframe is valid and clean.
        Modifies the dataframe in-place (e.g. removing exact duplicates) if safe.
        """
        if df is None or df.empty:
            logger.warning(f"Validation failed for {symbol}: Empty DataFrame.")
            return False

        is_valid = True
        
        # 1. Remove exact duplicate index entries
        initial_len = len(df)
        df = df[~df.index.duplicated(keep='last')]
        if len(df) < initial_len:
            logger.info(f"Removed {initial_len - len(df)} duplicate dates for {symbol}.")

        # 2. Check High < Low
        invalid_high_low = df[df['High'] < df['Low']]
        if not invalid_high_low.empty:
            logger.error(f"Validation failed for {symbol}: High < Low for {len(invalid_high_low)} rows.")
            is_valid = False

        # 3. Check for negative prices
        price_cols = ['Open', 'High', 'Low', 'Close']
        for col in price_cols:
            if (df[col] < 0).any():
                logger.error(f"Validation failed for {symbol}: Negative prices in {col}.")
                is_valid = False

        # 4. Check for invalid timestamps (e.g. future dates)
        future_dates = df[df.index > pd.Timestamp.now()]
        if not future_dates.empty:
            logger.error(f"Validation failed for {symbol}: Found {len(future_dates)} future dates.")
            is_valid = False

        return is_valid
