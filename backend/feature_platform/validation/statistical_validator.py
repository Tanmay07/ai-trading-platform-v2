import pandas as pd
import numpy as np

class StatisticalValidator:
    """
    Stage 3, 5, 6: Statistical Validation & Stability
    """
    def __init__(self):
        pass
        
    def validate_feature(self, df: pd.DataFrame, feature_col: str) -> dict:
        if feature_col not in df.columns:
            return {"valid": False}
            
        series = df[feature_col].replace([np.inf, -np.inf], np.nan).dropna()
        if series.empty:
            return {"valid": False, "stability_score": 0, "issues": ["No finite data"]}
            
        # 1. Basic Stats
        mean = series.mean()
        var = series.var()
        skew = series.skew()
        kurtosis = series.kurtosis()
        
        issues = []
        score = 100
        
        if np.abs(skew) > 10:
            issues.append(f"Highly skewed distribution: {skew:.2f}")
            score -= 10
            
        # 2. Time Stability (Characteristic Stability Index Proxy)
        # Split data into first half and second half, compare means/stds
        n = len(series)
        if n > 100:
            half = n // 2
            first_half = series.iloc[:half]
            second_half = series.iloc[half:]
            
            mean_diff = np.abs(first_half.mean() - second_half.mean())
            std_pooled = np.sqrt((first_half.var() + second_half.var()) / 2)
            
            if std_pooled > 0:
                # Cohen's d as a proxy for drift
                drift = mean_diff / std_pooled
                if drift > 1.0:
                    issues.append(f"High distribution drift detected (Cohen's d: {drift:.2f})")
                    score -= min(50, int(drift * 20))
        
        valid = score >= 60
        
        return {
            "valid": valid,
            "stability_score": max(score, 0),
            "issues": issues,
            "metrics": {
                "mean": float(mean),
                "var": float(var),
                "skew": float(skew),
                "kurtosis": float(kurtosis)
            }
        }
