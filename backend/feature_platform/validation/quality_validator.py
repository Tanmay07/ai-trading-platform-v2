import pandas as pd
import numpy as np

class QualityValidator:
    """
    Stage 1 & 10: Data Quality and Computational Cost Validation
    """
    def __init__(self, max_nan_pct=0.10):
        self.max_nan_pct = max_nan_pct
        
    def validate_feature(self, df: pd.DataFrame, feature_col: str) -> dict:
        if feature_col not in df.columns:
            return {"valid": False, "score": 0, "issues": ["Column missing"]}
            
        series = df[feature_col]
        score = 100
        issues = []
        
        # 1. Missing values
        nan_pct = series.isna().mean()
        if nan_pct > self.max_nan_pct:
            issues.append(f"High NaN percentage: {nan_pct:.1%}")
            score -= (nan_pct * 100) * 2
            
        # 2. Infinite values
        if np.isinf(series).any():
            issues.append("Contains infinite values")
            score -= 50
            
        # 3. Constant values
        if series.nunique(dropna=True) <= 1:
            issues.append("Zero variance (constant feature)")
            score -= 80
            
        # 4. Outliers (Z-score > 5)
        # Using a simple robust approximation (mean/std on finite data)
        finite_data = series.replace([np.inf, -np.inf], np.nan).dropna()
        if not finite_data.empty:
            mean = finite_data.mean()
            std = finite_data.std()
            if std > 0:
                z_scores = np.abs((finite_data - mean) / std)
                outlier_pct = (z_scores > 5).mean()
                if outlier_pct > 0.05:
                    issues.append(f"High outlier percentage: {outlier_pct:.1%}")
                    score -= (outlier_pct * 100)
                    
        # Complexity (Proxy: just based on categories later, default Lightweight here)
        comp_class = "Lightweight"
        
        valid = score >= 70
        return {
            "valid": valid,
            "quality_score": max(score, 0),
            "issues": issues,
            "nan_pct": nan_pct,
            "complexity": comp_class
        }
