import pandas as pd
import numpy as np

class VolatilityFeatures:
    """Calculates ATR, Bollinger Bands, Historical Volatility."""
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        return true_range.rolling(window=window).mean()
        
    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std: int = 2) -> pd.DataFrame:
        sma = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        # Band width and %B
        width = (upper_band - lower_band) / sma
        pct_b = (series - lower_band) / (upper_band - lower_band)
        
        return pd.DataFrame({
            'BB_Upper': upper_band,
            'BB_Lower': lower_band,
            'BB_Width': width,
            'BB_Pct_B': pct_b
        })
        
    @staticmethod
    def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df['ATR_14'] = VolatilityFeatures.calculate_atr(df, 14)
        
        bb_df = VolatilityFeatures.calculate_bollinger_bands(df['Close'], 20, 2)
        df = pd.concat([df, bb_df], axis=1)
        
        # Historical Volatility (Annualized based on 252 trading days)
        df['Daily_Return'] = df['Close'].pct_change()
        df['Hist_Vol_20'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
        
        return df
