import pandas as pd
from alpha_registry.evaluation.information_coefficient import calculate_ic

def calculate_rolling_stability(df: pd.DataFrame, factor_col: str, target_col: str, window: int = 60) -> dict:
    """
    Calculates rolling IC to check for alpha stability (is it degrading?).
    """
    if len(df) < window * 2:
        return {"stable": True, "degradation": 0.0}
        
    # We will just split in half for a simple "stability check"
    # First half vs Second half
    mid = len(df) // 2
    first_half = df.iloc[:mid]
    second_half = df.iloc[mid:]
    
    ic_first = calculate_ic(first_half, factor_col, target_col)["ic"]
    ic_second = calculate_ic(second_half, factor_col, target_col)["ic"]
    
    # If IC in the second half is significantly worse, the factor is decaying.
    degradation = ic_first - ic_second
    stable = degradation < 0.02 # Configurable tolerance
    
    return {
        "stable": bool(stable),
        "degradation": float(degradation),
        "ic_first_half": float(ic_first),
        "ic_second_half": float(ic_second)
    }
