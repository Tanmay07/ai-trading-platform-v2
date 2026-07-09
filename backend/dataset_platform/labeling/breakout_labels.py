import pandas as pd
import yaml

class BreakoutLabels:
    """
    Generates binary labels for breakout success.
    """
    def __init__(self):
        with open("config/dataset_platform.yaml", "r") as f:
            self.config = yaml.safe_load(f)["dataset_platform"]["labels"]["breakout"]
            
    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        horizon = self.config["forward_days"]
        target = self.config["target_pct"]
        
        # Calculate N-day forward return
        df[f'Target_{horizon}d_Return'] = (df['Close'].shift(-horizon) - df['Close']) / df['Close']
        
        # Binary: Did it hit the target % in N days?
        df[f'Target_{horizon}d_Breakout'] = (df[f'Target_{horizon}d_Return'] >= target).astype(int)
        
        return df
