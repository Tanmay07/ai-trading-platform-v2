import asyncio
from app.utils.logger import get_logger
from scripts.daily_suggestion_job import run_daily_job

logger = get_logger(__name__)

async def scheduled_suggestion_scan(interval_minutes: int = 120):
    """
    Runs the daily suggestion generation job every `interval_minutes` 
    and caches the results in S3.
    """
    logger.info(f"Started scheduled suggestion scan loop (interval: {interval_minutes}m)")
    
    while True:
        try:
            logger.info("Running scheduled suggestion scan...")
            
            # Run the synchronous ML job in a separate thread so it doesn't block FastAPI
            await asyncio.to_thread(run_daily_job)
                
            logger.info("Completed scheduled suggestion scan.")
                
        except asyncio.CancelledError:
            logger.info("Scheduled suggestion scan stopped.")
            break
        except Exception as e:
            logger.error(f"Error in scheduled suggestion scan: {e}")
            
        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)
