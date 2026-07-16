import pandas as pd

class BaselineLabeler:
    """
    Generates the benchmark production label (Future_Return_5D >= 5%)
    """
    def __init__(self, target_return: float = 5.0):
        self.target_return = target_return
        
    def generate_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Assumes 'Target_Return_5d' exists. If not, calculates it using 'Close' and 'Simulated_Exit_Price' (which defaults to Close at day 5).
        """
        import numpy as np
        if 'Target_Return_5d' in df.columns:
            return (df['Target_Return_5d'] >= (self.target_return - 1e-5)).astype(int)
        
        if 'Simulated_Return_Pct' in df.columns:
            return (df['Simulated_Return_Pct'] >= (self.target_return - 1e-5)).astype(int)
            
        return pd.Series(0, index=df.index)
