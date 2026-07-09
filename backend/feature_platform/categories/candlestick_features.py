import pandas as pd
import pandas_ta as ta

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Candlestick/Price Action Intelligence.
    Doji, Marubozu, Engulfing.
    """
    # Requires Open, High, Low, Close
    # Let pandas_ta handle basic pattern recognition
    cdl = ta.cdl_pattern(df['Open'], df['High'], df['Low'], df['Close'], name=["doji", "marubozu", "engulfing"])
    
    if cdl is not None and not cdl.empty:
        df = pd.concat([df, cdl], axis=1)
        
    # Gap %
    df['Gap_Pct'] = (df['Open'] - df['Close'].shift(1)) / df['Close'].shift(1)
    
    # Body Ratio
    df['Body_Ratio'] = abs(df['Close'] - df['Open']) / (df['High'] - df['Low']).replace(0, 1)
    
    return df
