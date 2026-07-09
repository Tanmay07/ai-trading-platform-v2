import pandas as pd
import pandas_ta as ta

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Momentum Factors using pandas_ta.
    RSI, MACD, PPO, ADX.
    """
    # RSI
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    
    # MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        df = pd.concat([df, macd], axis=1)
        
    # ADX
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    if adx is not None and not adx.empty:
        df = pd.concat([df, adx], axis=1)
        
    # Rate of Change
    df['ROC_10'] = ta.roc(df['Close'], length=10)
    
    return df
