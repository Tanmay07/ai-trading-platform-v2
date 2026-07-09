import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from data_platform.universe.universe_manager import UniverseManager
from data_platform.storage.postgres_manager import PostgresManager
from data_platform.storage.parquet_manager import ParquetManager
from data_platform.loaders.historical_loader import HistoricalLoader
from data_platform.loaders.incremental_loader import IncrementalLoader

logger = logging.getLogger(__name__)

class DataOrchestrator:
    """
    Central orchestrator for the Historical Data Platform.
    Ties together Universe, Loaders, Validators, and Storage.
    """

    def __init__(self):
        self.db = PostgresManager()
        self.parquet = ParquetManager()
        self.universe_manager = UniverseManager(db_manager=self.db)
        self.historical_loader = HistoricalLoader(db_manager=self.db, parquet_manager=self.parquet)
        self.incremental_loader = IncrementalLoader(db_manager=self.db, parquet_manager=self.parquet)

        self.jobs = {} # Keep track of running background jobs

    def run_bootstrap_sync(self, batch_size: int = 50, max_workers: int = 5, years: int = 10):
        """
        Runs a synchronous bootstrap of the active universe.
        """
        universe = self.universe_manager.fetch_active_universe()
        logger.info(f"Starting bootstrap for {len(universe)} symbols.")
        
        success_count = 0
        failed_count = 0

        # Run in parallel using a ThreadPool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.historical_loader.bootstrap_symbol, master.symbol, years): master.symbol
                for master in universe
            }

            for future in futures:
                symbol = futures[future]
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error executing bootstrap for {symbol}: {e}")
                    failed_count += 1

        logger.info(f"Bootstrap complete. Success: {success_count}, Failed: {failed_count}")
        return {"total": len(universe), "success": success_count, "failed": failed_count}

    def run_incremental_update_sync(self, max_workers: int = 5):
        """
        Runs a synchronous incremental update of the active universe.
        """
        universe = self.universe_manager.fetch_active_universe()
        logger.info(f"Starting incremental update for {len(universe)} symbols.")
        
        success_count = 0
        failed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.incremental_loader.update_symbol, master.symbol): master.symbol
                for master in universe
            }

            for future in futures:
                symbol = futures[future]
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error executing incremental update for {symbol}: {e}")
                    failed_count += 1

        logger.info(f"Incremental update complete. Success: {success_count}, Failed: {failed_count}")
        return {"total": len(universe), "success": success_count, "failed": failed_count}
        
    def get_data_quality_report(self) -> Dict[str, Any]:
        """
        Generates a quality report based on metadata.
        """
        universe = self.universe_manager.fetch_active_universe()
        total_symbols = len(universe)
        
        downloaded = 0
        total_rows = 0
        
        for master in universe:
            meta = self.db.get_metadata(master.symbol)
            if meta and meta.get("rows", 0) > 0:
                downloaded += 1
                total_rows += meta.get("rows", 0)
                
        return {
            "total_universe": total_symbols,
            "downloaded": downloaded,
            "pending": total_symbols - downloaded,
            "total_rows_stored": total_rows,
            "health_score": (downloaded / total_symbols * 100) if total_symbols > 0 else 0
        }
