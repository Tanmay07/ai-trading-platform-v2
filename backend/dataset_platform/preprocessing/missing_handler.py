import pandas as pd
import yaml
import logging

logger = logging.getLogger("MissingHandler")

class MissingHandler:
    def __init__(self):
        with open("config/dataset_platform.yaml", "r") as f:
            self.strategy = yaml.safe_load(f)["dataset_platform"]["preprocessing"]["missing_value_strategy"]
            
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        
        logger.info(f"Applying missing value strategy: {self.strategy}")
        
        if self.strategy == "forward_fill":
            return df.ffill().bfill() # bfill handles leading NaNs
        elif self.strategy == "median":
            # Only fill numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            return df
        elif self.strategy == "drop":
            return df.dropna()
        else:
            logger.warning(f"Unknown strategy {self.strategy}, falling back to forward_fill")
            return df.ffill().bfill()
