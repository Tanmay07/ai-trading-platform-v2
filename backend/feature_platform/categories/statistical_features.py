import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Statistical Factors.
    Rolling Mean, Std Dev, Skewness, Kurtosis.
    """
    # Z-Score of Close Price (20-day)
    df['Close_ZScore_20'] = (df['Close'] - df['Close'].rolling(20).mean()) / df['Close'].rolling(20).std()
    
    # Rolling Skew (requires min periods)
    df['Rolling_Skew_20'] = df['Close'].rolling(20).skew()
    
    # Rolling Kurtosis
    df['Rolling_Kurt_20'] = df['Close'].rolling(20).kurt()
    
    return df
