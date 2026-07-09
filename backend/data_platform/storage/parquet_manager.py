import pandas as pd
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ParquetManager:
    """Handles saving and loading OHLCV data as Parquet files locally."""

    def __init__(self, base_path: str = "data/historical_lake"):
        self.base_path = Path(base_path)
        self.equities_path = self.base_path / "historical" / "equities"
        self.equities_path.mkdir(parents=True, exist_ok=True)

    def save_symbol_data(self, df: pd.DataFrame, symbol: str) -> bool:
        """
        Saves DataFrame as a parquet file.
        Overwrites existing file. For huge datasets, we would append or partition by year.
        """
        if df.empty:
            return False
            
        file_path = self.equities_path / f"{symbol}.parquet"
        try:
            # We use engine='fastparquet' or 'pyarrow', Snappy compression is standard
            df.to_parquet(file_path, engine='pyarrow', compression='snappy')
            logger.info(f"Saved {len(df)} rows for {symbol} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save parquet for {symbol}: {e}")
            return False

    def load_symbol_data(self, symbol: str) -> pd.DataFrame:
        """Loads a symbol's historical data from Parquet."""
        file_path = self.equities_path / f"{symbol}.parquet"
        if not file_path.exists():
            return pd.DataFrame()
            
        try:
            df = pd.read_parquet(file_path, engine='pyarrow')
            return df
        except Exception as e:
            logger.error(f"Failed to load parquet for {symbol}: {e}")
            return pd.DataFrame()

    def append_symbol_data(self, df_new: pd.DataFrame, symbol: str) -> bool:
        """
        Appends new rows to an existing Parquet file.
        In Parquet, this requires loading, concatenating, and re-saving.
        """
        if df_new.empty:
            return True
            
        df_existing = self.load_symbol_data(symbol)
        if df_existing.empty:
            return self.save_symbol_data(df_new, symbol)
            
        # Concat and remove duplicates
        df_combined = pd.concat([df_existing, df_new])
        df_combined = df_combined[~df_combined.index.duplicated(keep='last')].sort_index()
        
        return self.save_symbol_data(df_combined, symbol)
