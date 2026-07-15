import os
import sys
import glob
from pathlib import Path
import asyncio

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from feature_platform.engine.feature_pipeline import FeaturePipeline
from dataset_platform.builder.dataset_generator import DatasetGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenerateAllFeatures")

async def generate_features():
    lake_path = Path("data/historical_lake/historical/equities/")
    files = glob.glob(str(lake_path / "*.parquet"))
    
    pipeline = FeaturePipeline()
    
    logger.info(f"Found {len(files)} historical parquets. Starting feature generation...")
    
    for i, file in enumerate(files):
        symbol = Path(file).stem
        logger.info(f"[{i+1}/{len(files)}] Processing {symbol}...")
        try:
            await pipeline.run_pipeline(symbol)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            
    logger.info("All features generated!")
    
    logger.info("Building full dataset_v1.parquet...")
    generator = DatasetGenerator()
    generator.build_dataset()
    logger.info("Done!")

if __name__ == "__main__":
    asyncio.run(generate_features())
