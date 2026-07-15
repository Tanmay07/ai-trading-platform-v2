import sys
import os
import asyncio
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model_training.training.training_pipeline import TrainingPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrainModel")

def main():
    logger.info("Triggering Training Pipeline...")
    pipeline = TrainingPipeline()
    version, metadata = pipeline.run_training()
    
    logger.info(f"Model successfully trained and registered as {version}")
    logger.info(f"Metrics: {metadata['metrics']}")

if __name__ == "__main__":
    main()
