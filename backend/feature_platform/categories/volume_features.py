import pandas as pd
import pandas_ta as ta

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Volume Intelligence.
    OBV, MFI, Delivery %.
    """
    # OBV
    df['OBV'] = ta.obv(df['Close'], df['Volume'])
    
    # MFI
    df['MFI_14'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
    
    # Relative Volume
    df['Volume_SMA_20'] = ta.sma(df['Volume'], length=20)
    df['Relative_Volume'] = df['Volume'] / df['Volume_SMA_20']
    
    return df
