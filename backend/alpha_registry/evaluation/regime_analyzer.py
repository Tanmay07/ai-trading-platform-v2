import pandas as pd
from alpha_registry.evaluation.information_coefficient import calculate_ic

def analyze_regime_performance(df: pd.DataFrame, factor_col: str, target_col: str) -> dict:
    """
    Splits the dataframe into Bull, Bear, and Sideways regimes (mock logic here)
    and evaluates the IC for each regime separately.
    """
    # Assuming 'Market_Regime' was populated by Phase D5/Feature Pipeline
    # For now we'll mock the split based on a simple 200 SMA on the index (or mock values)
    
    # Mocking regime split (random for architecture demonstration)
    bull_df = df.sample(frac=0.33) if not df.empty else df
    bear_df = df.sample(frac=0.33) if not df.empty else df
    
    ic_bull = calculate_ic(bull_df, factor_col, target_col)["ic"]
    ic_bear = calculate_ic(bear_df, factor_col, target_col)["ic"]
    
    return {
        "bull_regime_ic": ic_bull,
        "bear_regime_ic": ic_bear
    }
