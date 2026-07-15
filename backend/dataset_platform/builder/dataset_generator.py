import pandas as pd
import numpy as np
import logging
import os
from data_platform.universe.universe_manager import UniverseManager
from data_platform.universe.universe_db import UniverseDB
from feature_platform.storage.feature_store import FeatureStore

logger = logging.getLogger("DatasetGenerator")

class DatasetGenerator:
    def __init__(self):
        self.universe = UniverseManager(db_manager=UniverseDB())
        self.feature_store = FeatureStore()
        
    def generate_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates prediction labels for ML training.
        Requires Future data (Shifted negative).
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # 1. Regression Labels
        df['Target_Return_5d'] = (df['Close'].shift(-5) - df['Close']) / df['Close']
        df['Target_Return_7d'] = (df['Close'].shift(-7) - df['Close']) / df['Close']
        
        # 2. Classification Labels (Strong Buy to Strong Sell based on 5d return)
        def classify_return(ret):
            if pd.isna(ret): return np.nan
            if ret > 0.05: return 2   # Strong Buy (> 5%)
            if ret > 0.02: return 1   # Buy (2% to 5%)
            if ret < -0.05: return -2 # Strong Sell (< -5%)
            if ret < -0.02: return -1 # Sell (-2% to -5%)
            return 0                  # Hold (-2% to 2%)
            
        df['Target_Class_5d'] = df['Target_Return_5d'].apply(classify_return)
        
        # 3. Binary Labels (Breakout Success: >3% jump in next 5 days with no -2% drawdown)
        # We need a rolling future window for this. 
        # A simpler proxy for now: max high over next 5 days > 3% and min low over next 5 days > -2%
        future_high_max_5d = df['High'].shift(-5).rolling(window=5).max()
        future_low_min_5d = df['Low'].shift(-5).rolling(window=5).min()
        
        max_gain_pct = (future_high_max_5d - df['Close']) / df['Close']
        max_drawdown_pct = (future_low_min_5d - df['Close']) / df['Close']
        
        df['Target_Breakout_Success'] = ((max_gain_pct >= 0.03) & (max_drawdown_pct >= -0.02)).astype(float)
        # Handle NA at the end
        df.loc[df['Target_Return_5d'].isna(), 'Target_Breakout_Success'] = np.nan
        
        return df

    def build_dataset(self, output_path: str = "data/ml_datasets/dataset_v1.parquet"):
        logger.info("Starting Dataset Generation...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        active_symbols = [u.symbol for u in self.universe.fetch_active_universe()]
        all_data = []
        
        for i, symbol in enumerate(active_symbols):
            if i % 100 == 0:
                logger.info(f"Processing {i}/{len(active_symbols)} symbols...")
                
            parquet_path = self.feature_store._get_path(symbol)
            if not os.path.exists(parquet_path):
                continue
                
            df = pd.read_parquet(parquet_path)
            if df.empty: continue
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Generate labels
            df = self.generate_labels(df)
            
            # Drop rows with NA targets (the last 5-7 days of the dataset)
            df.dropna(subset=['Target_Return_7d', 'Target_Class_5d'], inplace=True)
            
            all_data.append(df)
            
        if not all_data:
            logger.error("No data found to build dataset.")
            return False
            
        final_df = pd.concat(all_data)
        
        # Write out
        final_df.to_parquet(output_path)
        logger.info(f"Dataset v1 generated successfully at {output_path} with {len(final_df)} rows and {len(final_df.columns)} columns.")
        return True
