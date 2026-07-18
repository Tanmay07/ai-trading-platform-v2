import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Risk Features using native pandas.
    """
    df = df.copy()
    
    returns = df['Close'].pct_change()
    
    # 1. Downside Deviation (20)
    downside_returns = returns.copy()
    downside_returns[downside_returns > 0] = 0
    df['Downside_Dev_20'] = downside_returns.rolling(20).std() * np.sqrt(252)
    
    # 2. Drawdown Risk
    rolling_max_252 = df['Close'].rolling(252, min_periods=1).max()
    df['Current_Drawdown'] = (df['Close'] - rolling_max_252) / rolling_max_252
    df['Max_Drawdown_252'] = df['Current_Drawdown'].rolling(252, min_periods=1).min()
    
    # 3. Sharpe & Sortino Proxies (20)
    ann_return = returns.rolling(20).mean() * 252
    ann_vol = returns.rolling(20).std() * np.sqrt(252)
    
    df['Sharpe_Proxy_20'] = ann_return / (ann_vol + 1e-10)
    df['Sortino_Proxy_20'] = ann_return / (df['Downside_Dev_20'] + 1e-10)
    
    # 4. Tail Risk (Proxy using 5th percentile of returns)
    df['Tail_Risk_5th_Pct_20'] = returns.rolling(20).quantile(0.05)
    
    # 5. Volatility-Adjusted Trend (Momentum / Volatility)
    mom_20 = (df['Close'] - df['Close'].shift(20)) / df['Close'].shift(20)
    df['Vol_Adjusted_Trend_20'] = mom_20 / (ann_vol + 1e-10)
    
    # 6. Stop-Loss Probability (Probability of hitting a 5% stop loss in next 5 days)
    # Approximated using current ATR
    atr14_pct = (df['High'] - df['Low']).ewm(com=13).mean() / df['Close']
    df['Stop_Loss_Prob_5Pct'] = 1 - np.exp(-5 * atr14_pct / 0.05)
    
    return df
