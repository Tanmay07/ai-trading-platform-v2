import pandas as pd
from scipy.stats import pearsonr, spearmanr
import logging

logger = logging.getLogger("InformationCoefficient")

def calculate_ic(df: pd.DataFrame, factor_col: str, target_col: str) -> dict:
    """
    Calculates the Information Coefficient (IC) and Rank IC for a single factor.
    IC measures the predictive power of a factor against future returns.
    """
    clean_df = df[[factor_col, target_col]].dropna()
    
    if len(clean_df) < 30:
        return {"ic": 0.0, "rank_ic": 0.0}
        
    try:
        # Pearson correlation (IC)
        ic, _ = pearsonr(clean_df[factor_col], clean_df[target_col])
        
        # Spearman rank correlation (Rank IC)
        rank_ic, _ = spearmanr(clean_df[factor_col], clean_df[target_col])
        
        return {
            "ic": float(ic) if not pd.isna(ic) else 0.0,
            "rank_ic": float(rank_ic) if not pd.isna(rank_ic) else 0.0
        }
    except Exception as e:
        logger.error(f"Error calculating IC for {factor_col}: {e}")
        return {"ic": 0.0, "rank_ic": 0.0}
