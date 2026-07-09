import pandas as pd
import numpy as np

class TechnicalFeatures:
    """Calculates EMAs, SMAs, MACD, RSI, etc."""
    
    @staticmethod
    def calculate_ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def calculate_sma(series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window=window).mean()
        
    @staticmethod
    def calculate_rsi(series: pd.Series, window: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50) # default neutral

    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        ema_fast = TechnicalFeatures.calculate_ema(series, fast)
        ema_slow = TechnicalFeatures.calculate_ema(series, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalFeatures.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'MACD_Line': macd_line,
            'MACD_Signal': signal_line,
            'MACD_Hist': histogram
        })
        
    @staticmethod
    def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
        """Adds all trend indicators to the dataframe."""
        df = df.copy()
        for span in [10, 20, 50, 100, 200]:
            df[f'EMA_{span}'] = TechnicalFeatures.calculate_ema(df['Close'], span)
        for window in [20, 50]:
            df[f'SMA_{window}'] = TechnicalFeatures.calculate_sma(df['Close'], window)
            
        df['RSI_14'] = TechnicalFeatures.calculate_rsi(df['Close'], 14)
        
        macd_df = TechnicalFeatures.calculate_macd(df['Close'])
        df = pd.concat([df, macd_df], axis=1)
        
        # Distance from EMAs (normalized)
        df['Dist_EMA_20'] = (df['Close'] - df['EMA_20']) / df['EMA_20']
        df['Dist_EMA_50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
        
        return df
