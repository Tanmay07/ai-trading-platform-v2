import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("CorrelationMatrix")

def generate_correlation_matrix(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Generates a Pearson correlation matrix across all feature columns.
    Helps identify duplicate factors (e.g. corr > 0.95).
    """
    if df.empty or not feature_cols:
        return pd.DataFrame()
        
    try:
        # Use pandas built-in corr
        corr_matrix = df[feature_cols].corr()
        return corr_matrix
    except Exception as e:
        logger.error(f"Failed to generate correlation matrix: {e}")
        return pd.DataFrame()
        
def identify_redundant_factors(corr_matrix: pd.DataFrame, threshold: float = 0.85) -> list:
    """
    Identifies pairs of features with correlation above the threshold.
    Returns a list of feature names that are candidates for removal.
    """
    if corr_matrix.empty:
        return []
        
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    # Find features where correlation is greater than the threshold
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column].abs() > threshold)]
    
    return to_drop
