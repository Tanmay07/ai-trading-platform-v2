import os
import sys
import glob
import logging
import asyncio
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_platform.loaders.bhavcopy_loader import BhavcopyLoader
from feature_platform.engine.feature_pipeline import FeaturePipeline
from dataset_platform.builder.dataset_generator import DatasetGenerator
from scripts.feature_governance import FeatureGovernancePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LivePipeline")

async def run_live_pipeline():
    logger.info("Starting Live Data Pipeline...")
    
    # 1. Fetch Latest Bhavcopy
    loader = BhavcopyLoader()
    target_date = datetime.today()
    bhavcopy_df = loader.fetch_bhavcopy(target_date)
    
    if bhavcopy_df.empty:
        logger.error("Failed to load Bhavcopy. Aborting pipeline.")
        return
        
    logger.info(f"Loaded Bhavcopy with {len(bhavcopy_df)} symbols.")
    
    # Use today's date for appending
    run_date = pd.to_datetime(target_date.date())
    
    lake_dir = Path("data/historical_lake/historical/equities")
    if not lake_dir.exists():
        logger.error(f"Historical lake not found at {lake_dir}")
        return
        
    existing_files = glob.glob(str(lake_dir / "*.parquet"))
    symbols_to_process = []
    
    logger.info("Updating Historical Lake...")
    # 2. Append to Historical Lake
    for file in existing_files:
        symbol = Path(file).stem
        symbol_row = bhavcopy_df[bhavcopy_df['Symbol'] == symbol]
        
        if not symbol_row.empty:
            row = symbol_row.iloc[0]
            try:
                hist_df = pd.read_parquet(file)
                if 'Date' in hist_df.index.names:
                    hist_df = hist_df.reset_index()
                
                # Check if date already exists
                if run_date not in hist_df['Date'].values:
                    new_row = {
                        'Date': run_date,
                        'Open': float(row['Open']),
                        'High': float(row['High']),
                        'Low': float(row['Low']),
                        'Close': float(row['Close']),
                        'Volume': float(row['Volume']),
                        'Dividends': 0.0,
                        'Stock Splits': 0.0
                    }
                    new_df = pd.DataFrame([new_row])
                    hist_df = pd.concat([hist_df, new_df], ignore_index=True)
                    
                    # Set index back to Date
                    hist_df.set_index('Date', inplace=True)
                    hist_df.to_parquet(file)
                    symbols_to_process.append(symbol)
            except Exception as e:
                logger.error(f"Failed to update {symbol}: {e}")
                
    logger.info(f"Updated {len(symbols_to_process)} symbols in historical lake.")
    
    if not symbols_to_process:
        logger.info("No new data to process. Pipeline finished.")
        return
        
    # 3. Run Feature Pipeline
    logger.info("Running Feature Pipeline...")
    feature_pipeline = FeaturePipeline()
    for i, symbol in enumerate(symbols_to_process):
        if i % 50 == 0:
            logger.info(f"Feature generation progress: {i}/{len(symbols_to_process)}")
        try:
            await feature_pipeline.run_pipeline(symbol)
        except Exception as e:
            logger.error(f"Failed feature pipeline for {symbol}: {e}")
            
    # 4. Build Dataset
    logger.info("Building V1/V3 Datasets...")
    generator = DatasetGenerator()
    generator.build_dataset()
    
    # 5. Run Feature Governance to output V5
    logger.info("Running Feature Governance Pipeline (generating dataset_v5)...")
    gov_pipeline = FeatureGovernancePipeline()
    gov_pipeline.run_pipeline()
    
    logger.info("Live Data Pipeline completed successfully. Dataset V5 is now up to date.")

if __name__ == "__main__":
    asyncio.run(run_live_pipeline())
