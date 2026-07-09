import pandas as pd
import numpy as np

class PriceActionFeatures:
    """Calculates gaps, candle shapes, and basic support/resistance distances."""
    
    @staticmethod
    def add_price_action_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Gap percentage
        df['Gap_Pct'] = (df['Open'] - df['Close'].shift()) / df['Close'].shift()
        
        # Candle shape
        df['Candle_Body'] = np.abs(df['Close'] - df['Open']) / df['Open']
        
        # High-low range
        daily_range = df['High'] - df['Low']
        
        # Upper and lower wicks
        upper_wick = df['High'] - np.maximum(df['Open'], df['Close'])
        lower_wick = np.minimum(df['Open'], df['Close']) - df['Low']
        
        # Avoid division by zero
        safe_range = daily_range.replace(0, np.nan)
        df['Upper_Wick_Ratio'] = upper_wick / safe_range
        df['Lower_Wick_Ratio'] = lower_wick / safe_range
        df['Upper_Wick_Ratio'] = df['Upper_Wick_Ratio'].fillna(0)
        df['Lower_Wick_Ratio'] = df['Lower_Wick_Ratio'].fillna(0)
        
        # Rolling Highs / Lows (Breakout proxies)
        df['Rolling_High_20'] = df['High'].rolling(window=20).max()
        df['Rolling_Low_20'] = df['Low'].rolling(window=20).min()
        
        # Distance to recent high (Resistance proxy)
        df['Dist_Res_20'] = (df['Rolling_High_20'] - df['Close']) / df['Close']
        
        # Distance to recent low (Support proxy)
        df['Dist_Sup_20'] = (df['Close'] - df['Rolling_Low_20']) / df['Close']
        
        return df
