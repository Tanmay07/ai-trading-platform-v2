import pandas as pd

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Time Features based on DatetimeIndex.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            return df
            
    df['DayOfWeek'] = df.index.dayofweek
    df['Month'] = df.index.month
    df['Quarter'] = df.index.quarter
    
    return df
