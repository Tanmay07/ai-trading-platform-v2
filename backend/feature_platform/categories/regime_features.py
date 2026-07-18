import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Market Regime Indicator features at the asset level.
    """
    df = df.copy()
    
    # 1. Bull/Bear/Sideways Probability (Simple HMM Proxy based on returns and vol)
    ret_20 = (df['Close'] - df['Close'].shift(20)) / df['Close'].shift(20)
    vol_20 = df['Close'].pct_change().rolling(20).std() * np.sqrt(252)
    
    # We use a logistic-style mapping as a proxy for regime probability
    df['Bull_Probability'] = 1 / (1 + np.exp(-10 * (ret_20 - 0.05)))
    df['Bear_Probability'] = 1 / (1 + np.exp(10 * (ret_20 + 0.05)))
    df['Sideways_Probability'] = 1.0 - (df['Bull_Probability'] + df['Bear_Probability']).clip(upper=1.0)
    
    # 2. Volatility Regime
    vol_100 = df['Close'].pct_change().rolling(100).std() * np.sqrt(252)
    df['Vol_Regime'] = np.where(vol_20 > vol_100 * 1.5, 2, # High Vol
                       np.where(vol_20 < vol_100 * 0.7, 0, # Low Vol
                       1)) # Normal Vol
                       
    # 3. Trend Persistence (Regime duration proxy)
    # Count consecutive days where EMA20 > EMA50 (Bull) or EMA20 < EMA50 (Bear)
    ema20 = df['Close'].ewm(span=20).mean()
    ema50 = df['Close'].ewm(span=50).mean()
    bull_flag = (ema20 > ema50).astype(int)
    
    persistence = np.zeros(len(df))
    for i in range(1, len(df)):
        if bull_flag.iloc[i] == bull_flag.iloc[i-1]:
            persistence[i] = persistence[i-1] + 1
        else:
            persistence[i] = 0
            
    df['Regime_Persistence_Days'] = persistence
    
    # Transition probability increases as persistence increases (mean reversion of regimes)
    df['Regime_Transition_Prob'] = 1 - np.exp(-df['Regime_Persistence_Days'] / 100)

    return df
