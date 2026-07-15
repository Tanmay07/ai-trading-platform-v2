import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("FeatureValidator")

class FeatureValidator:
    """
    Validates feature DataFrames for quality issues.
    """
    def __init__(self, max_nan_pct=0.10):
        self.max_nan_pct = max_nan_pct
        
    def validate(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {"valid": False, "score": 0, "issues": ["Empty DataFrame"]}
            
        issues = []
        score = 100
        metrics = {}
        
        # 1. Missing values (NaN)
        nan_pct = df.isna().mean()
        high_nan_cols = nan_pct[nan_pct > self.max_nan_pct].index.tolist()
        if high_nan_cols:
            issues.append(f"High NaN count in {len(high_nan_cols)} columns")
            score -= (len(high_nan_cols) * 2)
            
        # 2. Infinite values
        # Replace inf with nan temporarily just for counting
        inf_cols = []
        for col in df.select_dtypes(include=[np.number]).columns:
            if np.isinf(df[col]).any():
                inf_cols.append(col)
                
        if inf_cols:
            issues.append(f"Infinite values found in {len(inf_cols)} columns")
            score -= (len(inf_cols) * 5)
            
        # 3. Duplicate rows
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            issues.append(f"Found {dup_count} duplicate rows")
            score -= 10
            
        # 4. Constant features (excluding metadata columns like symbol if they exist)
        exclude_cols = ['symbol', 'Symbol', 'Date', 'date']
        check_cols = [c for c in df.columns if c not in exclude_cols]
        
        constant_cols = [col for col in check_cols if df[col].nunique(dropna=True) <= 1]
        if constant_cols:
            issues.append(f"Constant features found: {len(constant_cols)}")
            score -= (len(constant_cols) * 2)
            
        # 5. Invalid ranges (e.g. RSI outside 0-100)
        if 'RSI_14' in df.columns:
            if df['RSI_14'].max() > 100 or df['RSI_14'].min() < 0:
                issues.append("RSI_14 out of bounds (0-100)")
                score -= 5
                
        metrics = {
            "nan_columns": len(high_nan_cols),
            "inf_columns": len(inf_cols),
            "duplicate_rows": int(dup_count),
            "constant_columns": len(constant_cols),
            "total_columns": len(df.columns)
        }
        
        return {
            "valid": score >= 70,
            "score": max(score, 0),
            "issues": issues,
            "metrics": metrics
        }
