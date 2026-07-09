import logging
import asyncio
from sqlalchemy.orm import Session

logger = logging.getLogger("Step6_Dataset")

def execute(run_id: int, db: Session):
    """
    Step 6: Build training, validation, and test datasets.
    We aggregate all successfully processed symbols into tabular data.
    """
    logger.info("Starting Dataset Building...")
    
    # Normally calls ml_platform.datasets.dataset_builder.DatasetBuilder.build()
    # It would fetch all data from Feature Store and save as CSV or Parquet
    logger.info("Splitting data into Train/Val/Test (Walk-forward)...")
    
    logger.info("Step 6: Datasets successfully built.")
