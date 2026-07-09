import logging
from datetime import datetime, timedelta
import pandas as pd

from data_platform.providers.provider_factory import ProviderFactory
from data_platform.validation.data_validator import DataValidator
from data_platform.storage.parquet_manager import ParquetManager
from data_platform.storage.postgres_manager import PostgresManager

logger = logging.getLogger(__name__)

class IncrementalLoader:
    """
    Handles daily incremental updates to the historical data lake.
    """

    def __init__(self, db_manager: PostgresManager, parquet_manager: ParquetManager):
        self.db = db_manager
        self.parquet_manager = parquet_manager
        self.provider = ProviderFactory.get_provider()
        self.validator = DataValidator()

    def update_symbol(self, symbol: str) -> bool:
        """
        Fetches only the new trading days since the last_date in metadata.
        Appends them to the existing Parquet file.
        """
        metadata = self.db.get_metadata(symbol)
        if not metadata or not metadata.get("last_date"):
            logger.warning(f"No metadata found for {symbol}. Cannot run incremental update. Run bootstrap first.")
            return False

        last_date = metadata["last_date"]
        
        # We fetch from last_date to ensure we don't miss anything. Duplicate detector handles overlaps.
        start_date = last_date
        end_date = datetime.now()
        
        if (end_date - start_date).days < 1:
            logger.info(f"{symbol} is already up to date.")
            return True

        logger.info(f"Running incremental update for {symbol} from {start_date.date()} to {end_date.date()}")
        
        try:
            # 1. Download new data
            df_new = self.provider.get_symbol_history(symbol, start_date, end_date)
            
            if df_new.empty:
                logger.info(f"No new data found for {symbol}")
                return True
                
            # 2. Validate new data
            if not self.validator.validate_ohlcv(df_new, symbol):
                logger.error(f"Validation failed for incremental update of {symbol}")
                return False
                
            # 3. Append to Parquet
            if not self.parquet_manager.append_symbol_data(df_new, symbol):
                logger.error(f"Failed to append parquet data for {symbol}")
                return False
                
            # 4. Read back complete dataset to update metadata accurately
            df_full = self.parquet_manager.load_symbol_data(symbol)
            
            self.db.update_metadata(
                symbol=symbol,
                first_date=df_full.index.min(),
                last_date=df_full.index.max(),
                rows=len(df_full),
                provider=self.provider.provider_name()
            )
            
            logger.info(f"Successfully updated {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Incremental update failed for {symbol}: {e}")
            return False
