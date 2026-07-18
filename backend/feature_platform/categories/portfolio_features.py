import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Advanced Portfolio Context Features.
    In production, this would use the actual Nifty50 index data for calculation.
    """
    df = df.copy()
    
    returns = df['Close'].pct_change()
    
    # Mocking Nifty50 return as the asset's smoothed return for the prototype
    index_returns_proxy = returns.rolling(5).mean()
    
    # 1. Beta Contribution Proxy (60)
    # Covariance(Asset, Index) / Variance(Index)
    asset_var = returns.rolling(60).var()
    index_var = index_returns_proxy.rolling(60).var()
    covar = returns.rolling(60).cov(index_returns_proxy)
    
    df['Beta_60'] = covar / (index_var + 1e-10)
    
    # 2. Correlation Score (60)
    df['Index_Correlation_60'] = returns.rolling(60).corr(index_returns_proxy)
    
    # 3. Diversification Contribution
    # Negative correlation increases diversification contribution
    df['Diversification_Score'] = -1 * df['Index_Correlation_60']
    
    # 4. Idiosyncratic Risk (Asset Volatility that is unexplained by Beta)
    # Vol_asset^2 = Beta^2 * Vol_index^2 + Idiosyncratic_var
    asset_ann_var = asset_var * 252
    index_ann_var = index_var * 252
    
    idio_var = asset_ann_var - (df['Beta_60']**2 * index_ann_var)
    # Ensure no negative square roots due to approximation errors
    idio_var = idio_var.clip(lower=0)
    df['Idiosyncratic_Vol_60'] = np.sqrt(idio_var)

    return df
