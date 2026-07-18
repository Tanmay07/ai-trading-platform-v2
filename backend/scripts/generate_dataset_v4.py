import os
import sys
import pandas as pd
import numpy as np

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from feature_platform.engine.feature_engine import FeatureEngine
from feature_platform.categories.cross_sectional_features import generate_cross_sectional_features

def generate_mock_data(symbol: str, days: int = 1000) -> pd.DataFrame:
    """Generate mock historical data for testing the pipeline."""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    close = np.random.lognormal(mean=0.0002, sigma=0.015, size=days).cumprod() * 100
    high = close * np.random.uniform(1.0, 1.05, size=days)
    low = close * np.random.uniform(0.95, 1.0, size=days)
    open_p = (high + low) / 2
    volume = np.random.uniform(1e5, 1e7, size=days)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': open_p,
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume,
        'Symbol': symbol
    })
    df.set_index('Date', inplace=True)
    return df

def run_pipeline():
    print("Initializing Feature Engine...")
    engine = FeatureEngine()
    
    symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
    all_features = []
    
    print("Processing individual symbols...")
    for sym in symbols:
        df = generate_mock_data(sym)
        enhanced_df = engine.generate_features_for_df(df)
        all_features.append(enhanced_df)
        print(f"  Processed {sym} - shape: {enhanced_df.shape}")
        
    print("Combining for cross-sectional features...")
    combined_df = pd.concat(all_features)
    
    # Sort to ensure Date grouping works nicely
    combined_df.sort_index(inplace=True)
    
    print("Generating cross-sectional features...")
    final_df = generate_cross_sectional_features(combined_df)
    
    print(f"Final Dataset V4 shape: {final_df.shape}")
    print(f"Total features generated: {final_df.shape[1]}")
    
    # In production, this would be saved via parquet_manager to s3/gcs
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_v4.parquet')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_df.to_parquet(output_path)
    print(f"Successfully saved Dataset V4 to {output_path}")

if __name__ == "__main__":
    run_pipeline()
