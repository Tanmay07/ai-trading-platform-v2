import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Price Action Factors using native pandas.
    """
    df = df.copy()
    
    # 1. Swing High / Swing Low Detection (Window = 5)
    # A swing high is the highest high in a 5-day window centered on the current day
    high_roll = df['High'].rolling(window=5, center=True).max()
    low_roll = df['Low'].rolling(window=5, center=True).min()
    
    # Because of center=True, the last 2 days will be NaN. We forward fill for the features
    df['Is_Swing_High'] = (df['High'] == high_roll).astype(int).shift(2).fillna(0)
    df['Is_Swing_Low'] = (df['Low'] == low_roll).astype(int).shift(2).fillna(0)
    
    # 2. Higher Highs / Lower Lows (Trend Structure)
    # Get the last swing high/low prices
    df['Last_Swing_High'] = np.where(df['Is_Swing_High'] == 1, df['High'], np.nan)
    df['Last_Swing_High'] = df['Last_Swing_High'].ffill()
    
    df['Last_Swing_Low'] = np.where(df['Is_Swing_Low'] == 1, df['Low'], np.nan)
    df['Last_Swing_Low'] = df['Last_Swing_Low'].ffill()
    
    df['Higher_High'] = (df['Last_Swing_High'] > df['Last_Swing_High'].shift(1)).astype(int)
    df['Lower_Low'] = (df['Last_Swing_Low'] < df['Last_Swing_Low'].shift(1)).astype(int)
    
    # Market Structure Trend: 1 for HH/HL (Uptrend), -1 for LH/LL (Downtrend), 0 for mixed
    df['Structure_Trend'] = np.where(
        (df['Higher_High'] == 1) & (df['Lower_Low'] == 0), 1,
        np.where((df['Higher_High'] == 0) & (df['Lower_Low'] == 1), -1, 0)
    )
    
    # 3. Gap Classification
    prev_high = df['High'].shift(1)
    prev_low = df['Low'].shift(1)
    
    df['Gap_Up'] = (df['Open'] > prev_high).astype(int)
    df['Gap_Down'] = (df['Open'] < prev_low).astype(int)
    
    # Gap Size
    df['Gap_Size'] = np.where(df['Gap_Up'] == 1, (df['Open'] - prev_high) / prev_high,
                     np.where(df['Gap_Down'] == 1, (prev_low - df['Open']) / prev_low, 0.0))
                     
    # 4. Wick Statistics & Price Rejection
    body = abs(df['Close'] - df['Open'])
    total_range = df['High'] - df['Low']
    
    df['Upper_Wick'] = df['High'] - np.maximum(df['Close'], df['Open'])
    df['Lower_Wick'] = np.minimum(df['Close'], df['Open']) - df['Low']
    
    df['Upper_Wick_Ratio'] = df['Upper_Wick'] / (total_range + 1e-10)
    df['Lower_Wick_Ratio'] = df['Lower_Wick'] / (total_range + 1e-10)
    df['Body_Ratio'] = body / (total_range + 1e-10)
    
    # Rejection score: High score means long tail opposite to trend direction
    # Bullish rejection: Long lower wick, small body
    df['Bullish_Rejection'] = (df['Lower_Wick_Ratio'] > 0.5).astype(int) * df['Lower_Wick_Ratio']
    
    # Bearish rejection: Long upper wick, small body
    df['Bearish_Rejection'] = (df['Upper_Wick_Ratio'] > 0.5).astype(int) * df['Upper_Wick_Ratio']

    # 5. Consolidation Duration (Days since last 20-day high/low)
    highest_20 = df['High'].rolling(20).max()
    lowest_20 = df['Low'].rolling(20).min()
    
    is_new_high = (df['High'] == highest_20).astype(int)
    is_new_low = (df['Low'] == lowest_20).astype(int)
    
    # Count days since new high/low
    days_since_high = np.zeros(len(df))
    days_since_low = np.zeros(len(df))
    
    for i in range(1, len(df)):
        days_since_high[i] = 0 if is_new_high.iloc[i] == 1 else days_since_high[i-1] + 1
        days_since_low[i] = 0 if is_new_low.iloc[i] == 1 else days_since_low[i-1] + 1
        
    df['Days_Since_20d_High'] = days_since_high
    df['Days_Since_20d_Low'] = days_since_low
    
    # Consolidating if it hasn't made a new high or low in 10 days
    df['Is_Consolidating'] = ((df['Days_Since_20d_High'] > 10) & (df['Days_Since_20d_Low'] > 10)).astype(int)

    return df
