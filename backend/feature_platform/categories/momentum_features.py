import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Momentum Factors using native pandas.
    """
    df = df.copy()
    
    # 1. RSI (14) using Wilder's Smoothing
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 2. MACD (12, 26, 9)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
    # 3. ADX, +DI, -DI (14)
    high_diff = df['High'].diff()
    low_diff = -df['Low'].diff()
    
    plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0.0)
    minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0.0)
    
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift(1)).abs()
    tr3 = (df['Low'] - df['Close'].shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr14 = tr.ewm(com=13, adjust=False).mean()
    plus_di14 = 100 * (pd.Series(plus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14)
    minus_di14 = 100 * (pd.Series(minus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14)
    
    dx = 100 * (plus_di14 - minus_di14).abs() / (plus_di14 + minus_di14)
    adx14 = dx.ewm(com=13, adjust=False).mean()
    
    df['ADX_14'] = adx14
    df['Plus_DI_14'] = plus_di14
    df['Minus_DI_14'] = minus_di14
        
    # 4. Rate of Change (ROC) (10)
    df['ROC_10'] = (df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10) * 100
    
    # 5. Momentum (10)
    df['MOM_10'] = df['Close'] - df['Close'].shift(10)

    return df
