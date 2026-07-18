import pandas as pd
import numpy as np

class LeakageDetector:
    """
    Stage 2: Leakage Detection
    """
    def __init__(self, target_col: str = "Target_Forward_Return"):
        self.target_col = target_col
        
    def validate_feature(self, df: pd.DataFrame, feature_col: str) -> dict:
        if feature_col not in df.columns or self.target_col not in df.columns:
            return {"valid": False, "has_leakage": True, "reason": "Missing columns"}
            
        score = 100
        issues = []
        has_leakage = False
        
        series = df[feature_col]
        target = df[self.target_col]
        
        # We only check valid finite rows for correlation
        mask = np.isfinite(series) & np.isfinite(target)
        if mask.sum() > 30:
            # 1. Extreme correlation with target (almost identical)
            corr = np.abs(np.corrcoef(series[mask], target[mask])[0, 1])
            if corr > 0.98:
                issues.append(f"Target Leakage detected! Absolute correlation with future return: {corr:.3f}")
                has_leakage = True
                score = 0
                
            # 2. Exact match with future Close
            if 'Close' in df.columns:
                if 'Symbol' in df.columns:
                    future_close = df.groupby('Symbol')['Close'].shift(-1)
                else:
                    future_close = df['Close'].shift(-1)
                    
                match_mask = np.isfinite(series) & np.isfinite(future_close)
                if match_mask.sum() > 0:
                    exact_matches = np.isclose(series[match_mask], future_close[match_mask]).mean()
                    if exact_matches > 0.95:
                        issues.append("Future price leakage detected (Feature exactly matches tomorrow's close)")
                        has_leakage = True
                        score = 0
                        
        # 3. Naming convention checks
        name_lower = feature_col.lower()
        if "forward" in name_lower or "future" in name_lower or "next" in name_lower:
            # unless it's explicitly the target
            if feature_col != self.target_col:
                issues.append(f"Suspicious naming indicating future information: {feature_col}")
                # We flag it, but might not outright reject if it's a false positive, so slight penalty
                score -= 30
                
        return {
            "valid": not has_leakage,
            "leakage_score": score,
            "has_leakage": has_leakage,
            "issues": issues
        }
