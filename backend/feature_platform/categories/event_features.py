import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Simulated Event Features.
    In a live system, this would merge with an external corporate actions DB.
    """
    df = df.copy()
    
    # Mocking event features deterministically using the day of the year
    # E.g., earnings every 90 days.
    
    df['DayOfYear'] = df.index.dayofyear
    
    # 1. Earnings Proximity (Assume earnings on day 45, 135, 225, 315)
    earnings_days = np.array([45, 135, 225, 315])
    
    def dist_to_earnings(doy):
        # find closest future earnings day
        future_earnings = earnings_days[earnings_days >= doy]
        if len(future_earnings) > 0:
            return future_earnings[0] - doy
        else:
            return (365 - doy) + earnings_days[0]
            
    df['Days_To_Earnings'] = df['DayOfYear'].apply(dist_to_earnings)
    df['Is_Earnings_Week'] = (df['Days_To_Earnings'] <= 7).astype(int)
    
    # 2. Dividend Proximity (Assume dividend on day 100, 280)
    div_days = np.array([100, 280])
    def dist_to_div(doy):
        future_div = div_days[div_days >= doy]
        if len(future_div) > 0:
            return future_div[0] - doy
        else:
            return (365 - doy) + div_days[0]
            
    df['Days_To_Dividend'] = df['DayOfYear'].apply(dist_to_div)
    
    # 3. Event Importance & Decay (Simulated impact post-earnings)
    # Peaks at 1 on earnings day, decays exponentially
    days_since_earnings = 90 - df['Days_To_Earnings']
    df['Earnings_Impact_Decay'] = np.exp(-days_since_earnings / 10)
    
    df.drop(columns=['DayOfYear'], inplace=True)
    
    return df
