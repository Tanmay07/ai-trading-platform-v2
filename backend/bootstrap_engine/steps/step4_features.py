import logging
import asyncio
from sqlalchemy.orm import Session

from bootstrap_engine.state import SymbolTask

logger = logging.getLogger("Step4_Features")

async def execute(run_id: int, db: Session):
    """
    Step 4: Compute all features via Feature Store.
    """
    logger.info("Starting Feature Generation...")
    
    tasks = db.query(SymbolTask).filter(
        SymbolTask.run_id == run_id, 
        SymbolTask.step3_validation == "Success",
        SymbolTask.step4_features == "Pending"
    ).all()
    
    if not tasks:
        logger.info("No pending feature generations found. Skipping.")
        return
        
    logger.info(f"Generating features for {len(tasks)} symbols...")
    
    # MOCK ASYNC FEATURE GENERATION
    # Normally this calls ml_platform.feature_engineering
    await asyncio.sleep(2)
    
    for task in tasks:
        task.step4_features = "Success"
        
    db.commit()
    logger.info("Step 4: Feature generation complete.")
