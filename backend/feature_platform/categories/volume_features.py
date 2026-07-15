import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Volume Factors using native pandas.
    """
    df = df.copy()
    
    if 'Volume' not in df.columns or df['Volume'].empty:
        return df
        
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    
    # 1. Average Volume (20)
    df['Avg_Vol_20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    
    # 2. Relative Volume (20)
    df['Rel_Vol_20'] = df['Volume'] / df['Avg_Vol_20']
    
    # 3. OBV (On Balance Volume)
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    
    # 4. MFI (Money Flow Index 14)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    rmf = tp * df['Volume']
    
    delta_tp = tp.diff()
    pmf = np.where(delta_tp > 0, rmf, 0.0)
    nmf = np.where(delta_tp < 0, rmf, 0.0)
    
    pmf_sum = pd.Series(pmf, index=df.index).rolling(window=14).sum()
    nmf_sum = pd.Series(nmf, index=df.index).rolling(window=14).sum()
    
    mfi = 100 - (100 / (1 + (pmf_sum / nmf_sum)))
    df['MFI_14'] = mfi.fillna(50) # default to 50 if neutral
    
    # 5. VWAP and VWAP Distance
    rolling_vol = df['Volume'].rolling(window=20).sum()
    rolling_tp_vol = rmf.rolling(window=20).sum()
    df['VWAP_20'] = rolling_tp_vol / rolling_vol
    df['Dist_VWAP_20'] = (df['Close'] - df['VWAP_20']) / df['VWAP_20']
    
    # 6. Volume Spike Score (0 to 3 based on standard deviations of volume)
    vol_std = df['Volume'].rolling(window=20).std()
    z_score = (df['Volume'] - df['Avg_Vol_20']) / vol_std
    df['Vol_Spike_Score'] = pd.cut(z_score, bins=[-float('inf'), 1, 2, 3, float('inf')], labels=[0, 1, 2, 3]).astype(float).fillna(0)
    
    # 7. Volume Percentile (Rank of today's volume over last 20 days)
    # native pandas rank over rolling is slow, so we do a trick with rank
    def get_pct_rank(s):
        return pd.Series(s).rank(pct=True).iloc[-1]
    df['Vol_Percentile_20'] = df['Volume'].rolling(window=20).apply(get_pct_rank, raw=True)

    return df
