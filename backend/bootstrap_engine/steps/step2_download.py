import logging
import asyncio
from sqlalchemy.orm import Session
import yaml

from bootstrap_engine.state import SymbolTask

logger = logging.getLogger("Step2_Download")

with open("config/bootstrap.yaml", "r") as f:
    config = yaml.safe_load(f)["bootstrap"]

async def execute(run_id: int, db: Session):
    """
    Step 2: Download historical data for all symbols.
    Simulates a batched async download using Yahoo Finance.
    """
    logger.info("Starting Historical Download...")
    
    # Fetch pending tasks
    tasks = db.query(SymbolTask).filter(
        SymbolTask.run_id == run_id, 
        SymbolTask.step2_download == "Pending"
    ).all()
    
    if not tasks:
        logger.info("No pending downloads found. Skipping.")
        return
        
    logger.info(f"Found {len(tasks)} symbols to download.")
    batch_size = config.get("batch_size", 5)
    
    # Process in batches
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        logger.info(f"Downloading batch {i//batch_size + 1}...")
        
        # MOCK ASYNC DOWNLOAD
        # Normally this would call data_platform.providers.yahoo.YahooProvider.download()
        await asyncio.sleep(2) # simulate network latency
        
        for task in batch:
            # Mark as success
            task.step2_download = "Success"
            
        db.commit()
        
    logger.info("Step 2: Historical download complete.")
