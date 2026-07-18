import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Volatility Factors using native pandas.
    """
    df = df.copy()
    
    # 1. True Range & ATR
    tr = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    df['True_Range'] = tr
    df['ATR_14'] = df['True_Range'].ewm(com=13, adjust=False).mean()
    
    # 2. ATR Expansion & Breakout
    df['ATR_Avg_20'] = df['ATR_14'].rolling(window=20).mean()
    df['ATR_Expansion'] = df['ATR_14'] / df['ATR_Avg_20']
    df['Vol_Breakout_Score'] = (df['True_Range'] / df['ATR_14'])
    
    # 3. Bollinger Bands (20, 2)
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    std_20 = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (2 * std_20)
    df['BB_Lower'] = df['BB_Mid'] - (2 * std_20)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Mid']

    # 4. Parkinson Volatility (20)
    # sqrt( (1 / (4*n*ln(2))) * sum(ln(H/L)^2) )
    log_hl = np.log(df['High'] / df['Low'])**2
    df['Parkinson_Vol_20'] = np.sqrt( (1 / (4 * 20 * np.log(2))) * log_hl.rolling(20).sum() ) * np.sqrt(252)
    
    # 5. Garman-Klass Volatility (20)
    # 0.5 * ln(H/L)^2 - (2*ln(2)-1) * ln(C/O)^2
    term1 = 0.5 * np.log(df['High'] / df['Low'])**2
    term2 = (2 * np.log(2) - 1) * np.log(df['Close'] / df['Open'])**2
    df['Garman_Klass_Vol_20'] = np.sqrt((term1 - term2).rolling(20).mean()) * np.sqrt(252)
    
    # 6. Historical (Realized) Volatility (20)
    log_ret = np.log(df['Close'] / df['Close'].shift(1))
    df['Hist_Volatility_20'] = log_ret.rolling(window=20).std() * np.sqrt(252)
    
    # 7. Volatility Clustering / Compression
    # Compression: BB Width relative to historical BB Width
    df['BB_Width_Avg_100'] = df['BB_Width'].rolling(100).mean()
    df['Vol_Compression_Score'] = df['BB_Width'] / df['BB_Width_Avg_100']
    
    # 8. Ulcer Index (14) - Measure of downside volatility
    max_close_14 = df['Close'].rolling(14).max()
    drawdown = (df['Close'] - max_close_14) / max_close_14 * 100
    df['Ulcer_Index_14'] = np.sqrt((drawdown**2).rolling(14).mean())

    return df
