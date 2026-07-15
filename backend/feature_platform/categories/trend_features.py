import pandas as pd

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Trend Factors using native pandas.
    """
    df = df.copy()
    
    # 1. Moving Averages
    for length in [10, 20, 50, 100, 200]:
        df[f'EMA_{length}'] = df['Close'].ewm(span=length, adjust=False).mean()
    
    for length in [20, 50, 200]:
        df[f'SMA_{length}'] = df['Close'].rolling(window=length, min_periods=1).mean()
            
    # 2. Distance from EMA
    if 'EMA_20' in df.columns:
        df['Dist_EMA_20'] = (df['Close'] - df['EMA_20']) / df['EMA_20']
    if 'EMA_50' in df.columns:
        df['Dist_EMA_50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
    if 'EMA_200' in df.columns:
        df['Dist_EMA_200'] = (df['Close'] - df['EMA_200']) / df['EMA_200']
        
    # 3. EMA Slope (Rate of Change over 5 days)
    if 'EMA_20' in df.columns:
        df['EMA_20_Slope'] = (df['EMA_20'] - df['EMA_20'].shift(5)) / df['EMA_20'].shift(5)
    if 'EMA_50' in df.columns:
        df['EMA_50_Slope'] = (df['EMA_50'] - df['EMA_50'].shift(5)) / df['EMA_50'].shift(5)

    # 4. EMA Crossovers
    if 'EMA_50' in df.columns and 'EMA_200' in df.columns:
        df['Golden_Cross'] = ((df['EMA_50'] > df['EMA_200']) & (df['EMA_50'].shift(1) <= df['EMA_200'].shift(1))).astype(int)
        df['Death_Cross'] = ((df['EMA_50'] < df['EMA_200']) & (df['EMA_50'].shift(1) >= df['EMA_200'].shift(1))).astype(int)
        
    if 'EMA_20' in df.columns and 'EMA_50' in df.columns:
        df['Bull_Cross_20_50'] = ((df['EMA_20'] > df['EMA_50']) & (df['EMA_20'].shift(1) <= df['EMA_50'].shift(1))).astype(int)

    # 5. Price Above EMA Flags
    if 'EMA_20' in df.columns:
        df['Above_EMA_20'] = (df['Close'] > df['EMA_20']).astype(int)
    if 'EMA_50' in df.columns:
        df['Above_EMA_50'] = (df['Close'] > df['EMA_50']).astype(int)
    if 'EMA_200' in df.columns:
        df['Above_EMA_200'] = (df['Close'] > df['EMA_200']).astype(int)

    # 6. Trend Strength Score
    score = pd.Series(0, index=df.index)
    if 'EMA_20' in df.columns:
        score += (df['Close'] > df['EMA_20']).astype(int)
    if 'EMA_20' in df.columns and 'EMA_50' in df.columns:
        score += (df['EMA_20'] > df['EMA_50']).astype(int)
    if 'EMA_50' in df.columns and 'EMA_200' in df.columns:
        score += (df['EMA_50'] > df['EMA_200']).astype(int)
    
    df['Trend_Strength_Score'] = score

    return df
