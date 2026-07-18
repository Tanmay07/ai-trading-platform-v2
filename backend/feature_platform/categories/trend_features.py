import pandas as pd
import numpy as np

def _calc_hma(series: pd.Series, period: int) -> pd.Series:
    half_length = int(period / 2)
    sqrt_length = int(np.sqrt(period))
    wma_half = series.rolling(window=half_length).apply(lambda x: np.sum(x * np.arange(1, half_length + 1)) / np.sum(np.arange(1, half_length + 1)), raw=True)
    wma_full = series.rolling(window=period).apply(lambda x: np.sum(x * np.arange(1, period + 1)) / np.sum(np.arange(1, period + 1)), raw=True)
    diff = (2 * wma_half) - wma_full
    hma = diff.rolling(window=sqrt_length).apply(lambda x: np.sum(x * np.arange(1, sqrt_length + 1)) / np.sum(np.arange(1, sqrt_length + 1)), raw=True)
    return hma

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Trend Factors using native pandas.
    """
    df = df.copy()
    
    # 1. Moving Averages
    for length in [10, 20, 50, 100, 200]:
        df[f'EMA_{length}'] = df['Close'].ewm(span=length, adjust=False).mean()
        df[f'SMA_{length}'] = df['Close'].rolling(window=length, min_periods=1).mean()
        
        # Triple EMA (TEMA)
        ema1 = df['Close'].ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        ema3 = ema2.ewm(span=length, adjust=False).mean()
        df[f'TEMA_{length}'] = (3 * ema1) - (3 * ema2) + ema3

    # Hull Moving Average (HMA)
    df['HMA_20'] = _calc_hma(df['Close'], 20)
    df['HMA_50'] = _calc_hma(df['Close'], 50)

    # 2. Distance from EMA & TEMA
    df['Dist_EMA_20'] = (df['Close'] - df['EMA_20']) / df['EMA_20']
    df['Dist_EMA_50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
    df['Dist_EMA_200'] = (df['Close'] - df['EMA_200']) / df['EMA_200']
    
    df['Dist_TEMA_20'] = (df['Close'] - df['TEMA_20']) / df['TEMA_20']
    
    # 3. EMA Slope (Trend Acceleration)
    df['EMA_20_Slope'] = (df['EMA_20'] - df['EMA_20'].shift(5)) / df['EMA_20'].shift(5)
    df['EMA_50_Slope'] = (df['EMA_50'] - df['EMA_50'].shift(5)) / df['EMA_50'].shift(5)
    df['EMA_20_Acceleration'] = df['EMA_20_Slope'] - df['EMA_20_Slope'].shift(5)

    # 4. Donchian Channels
    df['Donchian_High_20'] = df['High'].rolling(window=20).max()
    df['Donchian_Low_20'] = df['Low'].rolling(window=20).min()
    df['Donchian_Mid_20'] = (df['Donchian_High_20'] + df['Donchian_Low_20']) / 2
    df['Price_to_Donchian_Mid'] = (df['Close'] - df['Donchian_Mid_20']) / df['Donchian_Mid_20']

    # 5. Keltner Channels (20, 2 ATR)
    tr = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    atr20 = pd.Series(tr).rolling(20).mean()
    df['Keltner_Upper_20'] = df['EMA_20'] + (2 * atr20)
    df['Keltner_Lower_20'] = df['EMA_20'] - (2 * atr20)
    df['Keltner_Position'] = (df['Close'] - df['Keltner_Lower_20']) / (df['Keltner_Upper_20'] - df['Keltner_Lower_20']) # 0 to 1

    # 6. Crossovers & Multi-timeframe Alignment
    df['Golden_Cross'] = ((df['EMA_50'] > df['EMA_200']) & (df['EMA_50'].shift(1) <= df['EMA_200'].shift(1))).astype(int)
    df['Death_Cross'] = ((df['EMA_50'] < df['EMA_200']) & (df['EMA_50'].shift(1) >= df['EMA_200'].shift(1))).astype(int)
    
    # Alignment: 10 > 20 > 50 > 200
    df['Trend_Alignment_Bullish'] = ((df['EMA_10'] > df['EMA_20']) & (df['EMA_20'] > df['EMA_50']) & (df['EMA_50'] > df['EMA_200'])).astype(int)
    df['Trend_Alignment_Bearish'] = ((df['EMA_10'] < df['EMA_20']) & (df['EMA_20'] < df['EMA_50']) & (df['EMA_50'] < df['EMA_200'])).astype(int)

    # 7. Choppiness Index (14)
    # 100 * LOG10( SUM(ATR(1), n) / ( MaxHi(n) - MinLo(n) ) ) / LOG10(n)
    n = 14
    sum_tr = pd.Series(tr).rolling(n).sum()
    max_hi = df['High'].rolling(n).max()
    min_lo = df['Low'].rolling(n).min()
    df['Choppiness_Index_14'] = 100 * np.log10(sum_tr / (max_hi - min_lo)) / np.log10(n)

    # 8. Trend Persistence & Exhaustion
    df['Up_Days'] = (df['Close'] > df['Close'].shift(1)).astype(int)
    df['Trend_Persistence_10'] = df['Up_Days'].rolling(10).sum() / 10.0
    
    # 9. SuperTrend Proxy (Basic MACD/ATR based combo)
    df['SuperTrend_Up'] = (df['Close'] > df['Keltner_Upper_20']).astype(int)
    df['SuperTrend_Down'] = (df['Close'] < df['Keltner_Lower_20']).astype(int)

    # 10. Trend Strength Score
    df['Trend_Strength_Score'] = (
        (df['Close'] > df['EMA_20']).astype(int) + 
        (df['EMA_20'] > df['EMA_50']).astype(int) + 
        (df['EMA_50'] > df['EMA_200']).astype(int) +
        df['Trend_Alignment_Bullish']
    )

    return df
