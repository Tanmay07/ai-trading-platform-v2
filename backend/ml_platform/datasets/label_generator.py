import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class LabelGenerator:
    """Generates future return labels for ML training."""
    
    @staticmethod
    def generate_labels(df: pd.DataFrame, horizons: list = [5, 7]) -> pd.DataFrame:
        """
        Adds forward return labels to the dataframe.
        Crucial: Shifting backwards means row at day T gets the return at day T+horizon.
        """
        df = df.copy()
        
        for horizon in horizons:
            # Future Return %
            # Note: We use shift(-horizon) to bring future close to current row
            future_close = df['Close'].shift(-horizon)
            df[f'Target_{horizon}d_Return'] = (future_close - df['Close']) / df['Close']
            
            # Classification Labels
            # Thresholds: Strong Buy > 5%, Buy > 2%, Hold -2 to 2%, Sell < -2%, Strong Sell < -5%
            def classify_return(ret):
                if pd.isna(ret):
                    return np.nan
                if ret >= 0.05: return 2     # Strong Buy
                elif ret >= 0.02: return 1   # Buy
                elif ret > -0.02: return 0   # Hold
                elif ret > -0.05: return -1  # Sell
                else: return -2              # Strong Sell
                
            df[f'Target_{horizon}d_Class'] = df[f'Target_{horizon}d_Return'].apply(classify_return)
            
            # Binary Breakout (Simple > 2% return)
            df[f'Target_{horizon}d_Breakout'] = (df[f'Target_{horizon}d_Return'] >= 0.02).astype(float)
            # Need to restore NaNs where target is NaN
            df.loc[df[f'Target_{horizon}d_Return'].isna(), f'Target_{horizon}d_Breakout'] = np.nan

        return df
