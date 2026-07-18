import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Volume Factors using native pandas.
    """
    df = df.copy()
    
    if 'Volume' not in df.columns or df['Volume'].empty:
        return df
        
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    
    # 1. Average Volume & RVOL
    df['Avg_Vol_20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Rel_Vol_20'] = df['Volume'] / (df['Avg_Vol_20'] + 1e-10)
    
    # Volume Acceleration
    df['Vol_10'] = df['Volume'].rolling(10).mean()
    df['Vol_50'] = df['Volume'].rolling(50).mean()
    df['Vol_Acceleration'] = df['Vol_10'] / (df['Vol_50'] + 1e-10)
    
    # 2. OBV (On Balance Volume)
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    df['OBV_EMA_20'] = df['OBV'].ewm(span=20, adjust=False).mean()
    df['OBV_Trend'] = (df['OBV'] - df['OBV_EMA_20']) / (df['OBV_EMA_20'].abs() + 1e-10)
    
    # 3. MFI (Money Flow Index 14)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    rmf = tp * df['Volume']
    delta_tp = tp.diff()
    pmf = np.where(delta_tp > 0, rmf, 0.0)
    nmf = np.where(delta_tp < 0, rmf, 0.0)
    pmf_sum = pd.Series(pmf, index=df.index).rolling(window=14).sum()
    nmf_sum = pd.Series(nmf, index=df.index).rolling(window=14).sum()
    mfi = 100 - (100 / (1 + (pmf_sum / (nmf_sum + 1e-10))))
    df['MFI_14'] = mfi.fillna(50) 
    
    # 4. VWAP Distance
    rolling_vol = df['Volume'].rolling(window=20).sum()
    rolling_tp_vol = rmf.rolling(window=20).sum()
    df['VWAP_20'] = rolling_tp_vol / (rolling_vol + 1e-10)
    df['Dist_VWAP_20'] = (df['Close'] - df['VWAP_20']) / (df['VWAP_20'] + 1e-10)
    
    # 5. Volume Spike Score
    vol_std = df['Volume'].rolling(window=20).std()
    z_score = (df['Volume'] - df['Avg_Vol_20']) / (vol_std + 1e-10)
    df['Vol_Spike_Score'] = pd.cut(z_score, bins=[-float('inf'), 1, 2, 3, float('inf')], labels=[0, 1, 2, 3]).astype(float).fillna(0)
    
    # 6. Accumulation/Distribution Line (ADL) & Chaikin Money Flow (CMF)
    clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'] + 1e-10)
    df['ADL'] = (clv * df['Volume']).cumsum()
    
    adl_20_sum = (clv * df['Volume']).rolling(20).sum()
    vol_20_sum = df['Volume'].rolling(20).sum()
    df['CMF_20'] = adl_20_sum / (vol_20_sum + 1e-10)
    
    # 7. Accumulation & Distribution Scores (Proxy based on price/vol divergence)
    up_vol = np.where(df['Close'] > df['Close'].shift(1), df['Volume'], 0)
    down_vol = np.where(df['Close'] < df['Close'].shift(1), df['Volume'], 0)
    df['Accumulation_Score'] = pd.Series(up_vol).rolling(14).sum() / (pd.Series(down_vol).rolling(14).sum() + 1e-10)
    
    # 8. Ease of Movement (EOM)
    # (H_t + L_t)/2 - (H_t-1 + L_t-1)/2 / (Volume_t / 100000000 / (H_t - L_t))
    midpt_move = ((df['High'] + df['Low']) / 2) - ((df['High'].shift(1) + df['Low'].shift(1)) / 2)
    box_ratio = (df['Volume'] / 100000000) / (df['High'] - df['Low'] + 1e-10)
    eom = midpt_move / (box_ratio + 1e-10)
    df['EOM_14'] = eom.rolling(14).mean()
    
    # 9. Smart Money Index Proxy
    # Smart money typically trades in the last hour; since we have daily data, we proxy it 
    # via close relative to open and high/low range combined with volume (similar to CLV but scaled).
    df['Smart_Money_Proxy'] = clv * np.log1p(df['Volume'])

    return df
