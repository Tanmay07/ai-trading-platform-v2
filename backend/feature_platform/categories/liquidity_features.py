import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Liquidity Factors.
    """
    df = df.copy()
    
    if 'Volume' not in df.columns or df['Volume'].empty:
        return df
        
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    
    # Typical price for value calculation
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    df['Daily_Traded_Value'] = typical_price * df['Volume']
    
    # 1. Average Daily Traded Value (20 days)
    df['Avg_Daily_Traded_Value_20'] = df['Daily_Traded_Value'].rolling(window=20, min_periods=1).mean()
    
    # 2. Average Daily Volume (20 days) - calculated in volume_features as well, but good to have here
    df['Avg_Daily_Volume_20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    
    # 3. Liquidity Score (0 to 1 based on percentile of traded value against a baseline)
    # A simple baseline is 100M INR. Above 100M is high liquidity (score 1). 
    # Let's map it smoothly using a log function or capping it.
    # We will just use the log10 of traded value as a simple continuous score
    df['Liquidity_Score'] = pd.Series(df['Avg_Daily_Traded_Value_20']).apply(lambda x: min(10.0, max(0.0, np.log10(x) - 5)) if x > 0 else 0)
    
    # 4. Tradability Score (Combination of Liquidity and Volatility)
    # If a stock is highly liquid and has decent volatility, it is highly tradable.
    # We can just normalize Liquidity Score for now.
    df['Tradability_Score'] = df['Liquidity_Score'] / 10.0
    
    # 5. Turnover Ratio (Volume / Outstanding Shares)
    # Since we don't have outstanding shares in standard OHLCV, we proxy it by Volume / Avg Volume
    df['Turnover_Ratio_Proxy'] = df['Volume'] / df['Avg_Daily_Volume_20']

    return df
