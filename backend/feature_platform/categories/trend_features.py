import pandas as pd
import pandas_ta as ta

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Trend Factors using pandas_ta.
    EMA (5,10,20,50,100,150,200), SMA, Ribbons, Crosses.
    """
    # Moving Averages
    for length in [5, 10, 20, 50, 100, 150, 200]:
        df[f'EMA_{length}'] = ta.ema(df['Close'], length=length)
        if length in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{length}'] = ta.sma(df['Close'], length=length)
            
    # Distance from EMA
    if 'EMA_20' in df.columns:
        df['Dist_EMA_20'] = (df['Close'] - df['EMA_20']) / df['EMA_20']
    if 'EMA_50' in df.columns:
        df['Dist_EMA_50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
        
    # Crossovers
    if 'EMA_50' in df.columns and 'EMA_200' in df.columns:
        df['Golden_Cross'] = (df['EMA_50'] > df['EMA_200']) & (df['EMA_50'].shift(1) <= df['EMA_200'].shift(1))
        df['Death_Cross'] = (df['EMA_50'] < df['EMA_200']) & (df['EMA_50'].shift(1) >= df['EMA_200'].shift(1))
        
    return df
