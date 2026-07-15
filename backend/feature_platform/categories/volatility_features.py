import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Volatility Factors using native pandas.
    """
    df = df.copy()
    
    # 1. True Range
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift(1)).abs()
    tr3 = (df['Low'] - df['Close'].shift(1)).abs()
    df['True_Range'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 2. ATR (14) - Wilder's Smoothing
    df['ATR_14'] = df['True_Range'].ewm(com=13, adjust=False).mean()
    
    # 3. ATR Expansion
    df['ATR_Avg_20'] = df['ATR_14'].rolling(window=20).mean()
    df['ATR_Expansion'] = df['ATR_14'] / df['ATR_Avg_20']
    df.drop(columns=['ATR_Avg_20'], inplace=True)
    
    # 4. Bollinger Bands (20, 2) and Bollinger Width
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    std_20 = df['Close'].rolling(window=20).std()
    
    df['BB_Upper'] = df['BB_Mid'] + (2 * std_20)
    df['BB_Lower'] = df['BB_Mid'] - (2 * std_20)
    
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Mid']

    # 5. Historical Volatility (20)
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Hist_Volatility_20'] = df['Log_Return'].rolling(window=20).std() * np.sqrt(252)
    df.drop(columns=['Log_Return'], inplace=True)
    
    # 6. Daily Range %
    df['Daily_Range_Pct'] = (df['High'] - df['Low']) / df['Low']

    return df
