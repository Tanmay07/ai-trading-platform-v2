import logging
import sys
import os

# Add the backend root to python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_platform.universe.universe_manager import UniverseManager
from data_platform.storage.postgres_manager import PostgresManager
from data_platform.storage.parquet_manager import ParquetManager
from data_platform.loaders.historical_loader import HistoricalLoader
from data_platform.universe.universe_db import UniverseDB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BatchDownloader")

def run_daily_batch(days_remaining: int = 7, years_of_history: int = 5):
    logger.info(f"Starting Historical Data Batch Downloader for {years_of_history} years of history.")
    
    universe = UniverseManager(db_manager=UniverseDB())
    db = PostgresManager()
    parquet = ParquetManager()
    loader = HistoricalLoader(db, parquet)
    
    universe_objects = universe.fetch_active_universe()
    active_symbols = [u.symbol for u in universe_objects]
    
    # Filter to only symbols we haven't successfully downloaded yet
    missing_symbols = []
    for sym in active_symbols:
        meta = db.get_metadata(sym)
        if not meta or meta.get("rows", 0) == 0:
            missing_symbols.append(sym)
            
    logger.info(f"Total active symbols: {len(active_symbols)}")
    logger.info(f"Symbols remaining to download: {len(missing_symbols)}")
    
    if not missing_symbols:
        logger.info("All symbols have been downloaded! Exiting.")
        return
        
    # Calculate batch size to complete in X days
    batch_size = max(1, len(missing_symbols) // days_remaining)
    logger.info(f"Days remaining: {days_remaining}. Target batch size for today: {batch_size}")
    
    symbols_to_process = missing_symbols[:batch_size]
    
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(symbols_to_process):
        logger.info(f"[{i+1}/{batch_size}] Downloading {symbol}...")
        success = loader.bootstrap_symbol(symbol, years=years_of_history)
        if success:
            success_count += 1
        else:
            fail_count += 1
            
    logger.info(f"Batch complete. Success: {success_count}, Failed: {fail_count}")
    logger.info(f"Remaining for tomorrow: {len(missing_symbols) - success_count}")

if __name__ == "__main__":
    # We can pass days remaining as arg, defaults to 7
    days = 7
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    run_daily_batch(days_remaining=days, years_of_history=5)
