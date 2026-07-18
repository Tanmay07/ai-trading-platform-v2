import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Momentum Factors using native pandas.
    """
    df = df.copy()
    
    # 1. Base RSI (14) using Wilder's Smoothing
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 2. Stochastic RSI (14, 14)
    min_rsi = df['RSI_14'].rolling(window=14).min()
    max_rsi = df['RSI_14'].rolling(window=14).max()
    df['StochRSI_14'] = (df['RSI_14'] - min_rsi) / (max_rsi - min_rsi + 1e-10) # 0 to 1

    # 3. Connors RSI (3, 2, 100)
    # 3a. RSI(3)
    c_ema_up = up.ewm(com=2, adjust=False).mean()
    c_ema_down = down.ewm(com=2, adjust=False).mean()
    df['RSI_3'] = 100 - (100 / (1 + (c_ema_up / c_ema_down)))
    
    # 3b. Up/Down Streak (2)
    streak = np.zeros(len(df))
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            streak[i] = streak[i-1] + 1 if streak[i-1] > 0 else 1
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            streak[i] = streak[i-1] - 1 if streak[i-1] < 0 else -1
        else:
            streak[i] = 0
    df['Streak'] = streak
    
    s_delta = df['Streak'].diff()
    s_up = s_delta.clip(lower=0)
    s_down = -1 * s_delta.clip(upper=0)
    s_ema_up = s_up.ewm(com=1, adjust=False).mean()
    s_ema_down = s_down.ewm(com=1, adjust=False).mean()
    df['RSI_Streak_2'] = 100 - (100 / (1 + (s_ema_up / s_ema_down)))
    
    # 3c. Percent Rank (100)
    roc_1 = df['Close'].diff() / df['Close'].shift(1)
    def percent_rank(x):
        return (x < x.iloc[-1]).sum() / len(x) * 100
    df['Percent_Rank_100'] = roc_1.rolling(100).apply(percent_rank, raw=False)
    
    df['ConnorsRSI'] = (df['RSI_3'] + df['RSI_Streak_2'] + df['Percent_Rank_100']) / 3

    # 4. MACD (12, 26, 9)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
    # 5. ADX, +DI, -DI (14)
    high_diff = df['High'].diff()
    low_diff = -df['Low'].diff()
    
    plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0.0)
    minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0.0)
    
    tr = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr14 = pd.Series(tr).ewm(com=13, adjust=False).mean()
    
    plus_di14 = 100 * (pd.Series(plus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14)
    minus_di14 = 100 * (pd.Series(minus_dm, index=df.index).ewm(com=13, adjust=False).mean() / atr14)
    
    dx = 100 * (plus_di14 - minus_di14).abs() / (plus_di14 + minus_di14)
    df['ADX_14'] = dx.ewm(com=13, adjust=False).mean()
    df['Plus_DI_14'] = plus_di14
    df['Minus_DI_14'] = minus_di14
        
    # 6. Rate of Change (ROC) & Acceleration
    df['ROC_10'] = (df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10) * 100
    df['ROC_20'] = (df['Close'] - df['Close'].shift(20)) / df['Close'].shift(20) * 100
    
    df['ROC_10_Acc'] = df['ROC_10'] - df['ROC_10'].shift(5) # Momentum Acceleration
    
    # 7. Price Velocity
    df['Price_Velocity'] = df['Close'].diff()
    df['Price_Acceleration'] = df['Price_Velocity'].diff()
    
    # 8. Rolling Momentum Consistency (What % of last 20 days had positive return?)
    df['Pos_Return'] = (df['Close'] > df['Close'].shift(1)).astype(int)
    df['Mom_Consistency_20'] = df['Pos_Return'].rolling(20).mean()

    return df
