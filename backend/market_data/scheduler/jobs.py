import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from market_data.service import MarketDataService

logger = logging.getLogger(__name__)

class MarketDataScheduler:
    def __init__(self, service: MarketDataService):
        self.scheduler = AsyncIOScheduler()
        self.service = service
        
    def setup_jobs(self):
        # 1. Daily symbol sync
        self.scheduler.add_job(self.sync_symbols, 'cron', hour=1, minute=0)
        # 2. Bhavcopy ingestion (End of day)
        self.scheduler.add_job(self.ingest_bhavcopy, 'cron', hour=18, minute=30)
        # 3. Market status check (every 10 min)
        self.scheduler.add_job(self.update_market_status, 'interval', minutes=10)
        
    def start(self):
        self.setup_jobs()
        self.scheduler.start()
        logger.info("MarketDataScheduler started.")
        
    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("MarketDataScheduler shutdown.")
        
    async def sync_symbols(self):
        logger.info("Scheduler: Running daily symbol sync...")
        # To be implemented with Provider
        
    async def ingest_bhavcopy(self):
        logger.info("Scheduler: Running Bhavcopy ingestion pipeline...")
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "run_live_pipeline.py")
        try:
            # Run the pipeline script as a separate process to avoid blocking the main event loop too much
            # though it uses asyncio internally.
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info(f"Bhavcopy Pipeline Success:\n{stdout.decode()}")
            else:
                logger.error(f"Bhavcopy Pipeline Failed:\n{stderr.decode()}")
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
        
    async def update_market_status(self):
        status = self.service.get_market_status()
        logger.info(f"Scheduler: Market status is {status.status}")
