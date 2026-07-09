import pandas as pd
import pandas_ta as ta

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Volatility Factors using pandas_ta.
    ATR, Bollinger Bands, Donchian Channels.
    """
    # ATR
    df['ATR_14'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    if 'ATR_14' in df.columns:
        df['ATR_Expansion'] = df['ATR_14'] / df['ATR_14'].rolling(20).mean()
        
    # Bollinger Bands
    bbands = ta.bbands(df['Close'], length=20, std=2)
    if bbands is not None and not bbands.empty:
        df = pd.concat([df, bbands], axis=1)
        
    # Donchian Channels
    donchian = ta.donchian(df['High'], df['Low'], lower_length=20, upper_length=20)
    if donchian is not None and not donchian.empty:
        df = pd.concat([df, donchian], axis=1)
        
    return df
