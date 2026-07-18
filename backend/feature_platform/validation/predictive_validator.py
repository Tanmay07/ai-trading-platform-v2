import pandas as pd
import numpy as np
from scipy.stats import spearmanr

class PredictiveValidator:
    """
    Stage 4: Predictive Power Analysis
    """
    def __init__(self, target_col: str = "Target_Forward_Return"):
        self.target_col = target_col
        
    def validate_feature(self, df: pd.DataFrame, feature_col: str) -> dict:
        if feature_col not in df.columns or self.target_col not in df.columns:
            return {"valid": False}
            
        series = df[feature_col]
        target = df[self.target_col]
        
        mask = np.isfinite(series) & np.isfinite(target)
        if mask.sum() < 30:
            return {"valid": False, "predictive_score": 0, "issues": ["Insufficient data for IC"]}
            
        # 1. Information Coefficient (Spearman Rank Correlation)
        ic, p_value = spearmanr(series[mask], target[mask])
        
        # 2. Mutual Information Proxy (Absolute IC * Non-linear scaling)
        # To avoid heavy sklearn computation on 160 features x 750 stocks in prototyping
        mi_proxy = np.abs(ic) * 1.5 
        
        issues = []
        score = 0
        
        # Scoring based on absolute IC
        abs_ic = np.abs(ic)
        if abs_ic < 0.01:
            issues.append(f"Very low predictive power (IC: {ic:.4f})")
            score = 20 # Poor
        elif abs_ic < 0.03:
            score = 50 # Weak
        elif abs_ic < 0.05:
            score = 75 # Good
        else:
            score = 100 # Excellent
            
        # Require minimal IC for strict production
        valid = score >= 50
            
        return {
            "valid": valid,
            "predictive_score": score,
            "issues": issues,
            "metrics": {
                "ic": float(ic),
                "ic_pvalue": float(p_value),
                "mi_proxy": float(mi_proxy)
            }
        }
