import pandas as pd
import yaml

class VolatilitySplitter:
    """
    Splits dataset based on ATR or VIX (using ATR proxy if VIX unavailable).
    """
    def __init__(self):
        with open("config/scenario_dataset.yaml", "r") as f:
            self.config = yaml.safe_load(f)["scenario_datasets"]["volatility"]
            
    def split(self, df: pd.DataFrame, level: str) -> pd.DataFrame:
        if df.empty or 'ATR_14' not in df.columns:
            return pd.DataFrame()
            
        # We calculate the percentile across the dataset for ATR_14
        if level == "high":
            threshold = df['ATR_14'].quantile(self.config["high"] / 100.0)
            return df[df['ATR_14'] >= threshold]
        elif level == "low":
            threshold = df['ATR_14'].quantile(self.config["low"] / 100.0)
            return df[df['ATR_14'] <= threshold]
            
        return pd.DataFrame()
