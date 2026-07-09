import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Breakout Intelligence.
    Distance from highs, NR7, Inside Bar, Consolidation.
    """
    # Distance from Highs
    df['High_20d'] = df['High'].rolling(20).max()
    df['Dist_High_20d'] = (df['High_20d'] - df['Close']) / df['Close']
    
    df['High_50d'] = df['High'].rolling(50).max()
    df['Dist_High_50d'] = (df['High_50d'] - df['Close']) / df['Close']
    
    # Range Expansion/Compression (NR7)
    df['Daily_Range'] = df['High'] - df['Low']
    df['NR7'] = (df['Daily_Range'] < df['Daily_Range'].rolling(7).min().shift(1)).astype(int)
    
    # Inside Bar
    df['Inside_Bar'] = ((df['High'] < df['High'].shift(1)) & (df['Low'] > df['Low'].shift(1))).astype(int)
    
    return df
