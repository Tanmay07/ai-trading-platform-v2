import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Breakout Factors using native pandas.
    """
    df = df.copy()
    
    # 1. Distance from Highs/Lows
    df['High_20'] = df['High'].rolling(window=20).max()
    df['High_50'] = df['High'].rolling(window=50).max()
    df['Low_20'] = df['Low'].rolling(window=20).min()
    
    df['Dist_High_20'] = (df['High_20'] - df['Close']) / df['Close']
    df['Dist_High_50'] = (df['High_50'] - df['Close']) / df['Close']
    df['Dist_Low_20'] = (df['Close'] - df['Low_20']) / df['Low_20']
    
    # Clean up intermediate cols
    df.drop(columns=['High_20', 'High_50', 'Low_20'], inplace=True)
    
    # 2. Range Compression Score
    if 'ATR_14' not in df.columns:
        tr1 = df['High'] - df['Low']
        tr2 = (df['High'] - df['Close'].shift(1)).abs()
        tr3 = (df['Low'] - df['Close'].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['ATR_14'] = tr.ewm(com=13, adjust=False).mean()
        
    df['Range_Compression'] = (df['High'] - df['Low']) / df['ATR_14']
    
    # 3. Consolidation Score
    df['Consolidation_Score'] = df['Close'].rolling(window=20).std() / df['Close'].rolling(window=20).mean()
    
    # 4. NR7 Detection
    daily_range = df['High'] - df['Low']
    min_range_7 = daily_range.rolling(window=7).min()
    df['NR7_Flag'] = (daily_range <= min_range_7).astype(int)
    
    # 5. Inside Bar Detection
    df['Inside_Bar_Flag'] = ((df['High'] < df['High'].shift(1)) & (df['Low'] > df['Low'].shift(1))).astype(int)
    
    # 6. Breakout Score
    score = pd.Series(0, index=df.index)
    score += (df['Dist_High_20'] <= 0.01).astype(int)
    
    if 'Volume' in df.columns:
        avg_vol = df['Volume'].rolling(window=20).mean()
        score += (df['Volume'] > avg_vol * 1.5).astype(int)
        
    score += (df['Range_Compression'] > 1.5).astype(int)
    score += (df['Close'] > df['Open']).astype(int)
    
    df['Breakout_Score'] = score

    return df
