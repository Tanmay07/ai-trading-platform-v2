import pandas as pd
import logging

logger = logging.getLogger("QualityValidator")

class QualityValidator:
    """
    Evaluates ML Dataset readiness.
    Calculates missing ratios, class balance, etc.
    """
    def __init__(self):
        pass
        
    def validate(self, df: pd.DataFrame, label_col: str = None) -> dict:
        if df.empty:
            return {"score": 0.0, "valid": False}
            
        score = 100.0
        issues = []
        
        # Missing %
        missing_pct = df.isna().mean().mean()
        if missing_pct > 0.05:
            score -= (missing_pct * 100) * 2
            issues.append(f"High missing values: {missing_pct:.1%}")
            
        # Class Balance
        if label_col and label_col in df.columns:
            if df[label_col].nunique() > 2: # Multi-class
                distribution = df[label_col].value_counts(normalize=True)
                min_class = distribution.min()
                if min_class < 0.05:
                    score -= 10
                    issues.append(f"Imbalanced classes. Smallest class is {min_class:.1%}")
                    
        return {
            "score": max(0.0, score),
            "valid": score >= 80.0,
            "issues": issues,
            "rows": len(df),
            "columns": len(df.columns)
        }
