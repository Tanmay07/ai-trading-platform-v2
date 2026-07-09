import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from data_platform.providers.provider_factory import ProviderFactory
from data_platform.validation.data_validator import DataValidator
from data_platform.storage.parquet_manager import ParquetManager
from data_platform.storage.postgres_manager import PostgresManager

logger = logging.getLogger(__name__)

class HistoricalLoader:
    """
    Downloads historical data for the equity universe (bootstrap).
    """

    def __init__(self, db_manager: PostgresManager, parquet_manager: ParquetManager):
        self.db = db_manager
        self.parquet_manager = parquet_manager
        self.provider = ProviderFactory.get_provider()
        self.validator = DataValidator()

    def bootstrap_symbol(self, symbol: str, years: int = 10) -> bool:
        """
        Downloads `years` of historical data for a specific symbol.
        Retries on failure with exponential backoff.
        """
        logger.info(f"Starting bootstrap download for {symbol} ({years} years)")
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(years=years)
        
        # Check if already downloaded
        metadata = self.db.get_metadata(symbol)
        if metadata and metadata.get("rows", 0) > 0:
            logger.info(f"Symbol {symbol} already bootstrapped. Skipping.")
            return True

        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # 1. Download
                df = self.provider.get_symbol_history(symbol, start_date, end_date)
                
                if df.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return False
                
                # 2. Validate
                if not self.validator.validate_ohlcv(df, symbol):
                    logger.error(f"Validation failed for {symbol} during bootstrap.")
                    return False
                    
                # 3. Store in Parquet
                if not self.parquet_manager.save_symbol_data(df, symbol):
                    logger.error(f"Failed to save parquet for {symbol}")
                    return False
                    
                # 4. Update Metadata DB
                self.db.update_metadata(
                    symbol=symbol,
                    first_date=df.index.min(),
                    last_date=df.index.max(),
                    rows=len(df),
                    provider=self.provider.provider_name()
                )
                
                logger.info(f"Successfully bootstrapped {symbol}")
                return True
                
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed for {symbol}: {e}")
                time.sleep(retry_delay * (2 ** attempt)) # Exponential backoff
                
        logger.error(f"Failed to bootstrap {symbol} after {max_retries} attempts.")
        return False
