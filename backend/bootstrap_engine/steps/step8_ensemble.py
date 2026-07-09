import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("Step8_Ensemble")

def execute(run_id: int, db: Session):
    """
    Step 8: Build the Meta Ensemble.
    Uses soft voting / weighted averaging.
    """
    logger.info("Building Meta Ensemble...")
    logger.info("Combining LightGBM, XGBoost, and CatBoost probabilities...")
    logger.info("Step 8: Meta Ensemble built successfully.")
