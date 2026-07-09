import pandas as pd
import numpy as np

class VolumeFeatures:
    """Calculates OBV, VWAP, Relative Volume."""
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        # On-Balance Volume
        obv = np.where(df['Close'] > df['Close'].shift(), df['Volume'], 
                       np.where(df['Close'] < df['Close'].shift(), -df['Volume'], 0))
        return pd.Series(obv, index=df.index).cumsum()
        
    @staticmethod
    def calculate_vwap(df: pd.DataFrame, window: int = 14) -> pd.Series:
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        # In a real system, VWAP is usually intraday (reset daily). 
        # For end-of-day data, a rolling VWAP is often used.
        vol_price = typical_price * df['Volume']
        return vol_price.rolling(window=window).sum() / df['Volume'].rolling(window=window).sum()

    @staticmethod
    def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Volume SMA and Relative Volume
        df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Rel_Volume'] = df['Volume'] / df['Vol_SMA_20']
        
        # Replace inf/nan caused by zero volume
        df['Rel_Volume'] = df['Rel_Volume'].replace([np.inf, -np.inf], np.nan).fillna(1.0)
        
        df['OBV'] = VolumeFeatures.calculate_obv(df)
        df['VWAP_14'] = VolumeFeatures.calculate_vwap(df, 14)
        
        # OBV trend
        df['OBV_SMA_20'] = df['OBV'].rolling(window=20).mean()
        
        return df
