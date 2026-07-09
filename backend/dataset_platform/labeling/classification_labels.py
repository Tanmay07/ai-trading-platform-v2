import pandas as pd
import yaml

class ClassificationLabels:
    """
    Generates multi-class labels: Strong Buy, Buy, Hold, Sell, Strong Sell.
    """
    def __init__(self):
        with open("config/dataset_platform.yaml", "r") as f:
            self.config = yaml.safe_load(f)["dataset_platform"]["labels"]["classification"]
            
    def generate(self, df: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
        # Calculate N-day forward return
        col_name = f'Target_{horizon}d_Return'
        if col_name not in df.columns:
            df[col_name] = (df['Close'].shift(-horizon) - df['Close']) / df['Close']
            
        def categorize(val):
            if pd.isna(val): return None
            if val >= self.config["strong_buy"]: return "Strong Buy"
            if val >= self.config["buy"]: return "Buy"
            if val <= self.config["strong_sell"]: return "Strong Sell"
            if val <= self.config["sell"]: return "Sell"
            return "Hold"
            
        df[f'Target_{horizon}d_Class'] = df[col_name].apply(categorize)
        
        # Also create a numeric version for ML models
        mapping = {"Strong Sell": 0, "Sell": 1, "Hold": 2, "Buy": 3, "Strong Buy": 4}
        df[f'Target_{horizon}d_ClassNum'] = df[f'Target_{horizon}d_Class'].map(mapping)
        
        return df
