import pandas as pd
import yaml

class MarketRegimeSplitter:
    """
    Splits a dataset based on broad market regimes (e.g. Bull vs Bear).
    Uses a simplistic Moving Average strategy on the Nifty 50 for this simulation.
    In a real environment, this would pull from the Historical Data Platform's ^NSEI ticker.
    """
    def __init__(self):
        with open("config/scenario_dataset.yaml", "r") as f:
            self.config = yaml.safe_load(f)["scenario_datasets"]["regimes"]
            
    def split(self, df: pd.DataFrame, regime_name: str) -> pd.DataFrame:
        """
        Since we don't have the Index data natively merged into every symbol row yet,
        we will simulate regime filtering based on the config logic if the index data existed.
        For demonstration, we assume a synthetic 'Index_SMA_Fast' and 'Index_SMA_Slow' exist, 
        or we generate a proxy regime based on the stock's own MAs if index isn't available.
        """
        if df.empty:
            return df
            
        # Fallback to stock's own Trend if Index data is missing in the dataset
        fast_col = f"SMA_{self.config[regime_name]['sma_fast']}"
        slow_col = f"SMA_{self.config[regime_name]['sma_slow']}"
        
        # If the features exist, apply the filter
        if fast_col in df.columns and slow_col in df.columns:
            if self.config[regime_name]['condition'] == "fast > slow":
                return df[df[fast_col] > df[slow_col]]
            else:
                return df[df[fast_col] < df[slow_col]]
                
        # If columns don't exist, return empty to prevent generating invalid scenarios
        return pd.DataFrame()
