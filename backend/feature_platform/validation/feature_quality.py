import pandas as pd
import logging
import yaml

logger = logging.getLogger("FeatureQuality")

class FeatureQualityValidator:
    """
    Evaluates DataFrames for NaN spikes, infinites, or constant values.
    """
    def __init__(self):
        with open("config/feature_store.yaml", "r") as f:
            self.config = yaml.safe_load(f)["feature_store"]["quality"]
            
    def validate(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {"valid": False, "score": 0, "issues": ["Empty DataFrame"]}
            
        issues = []
        score = 100
        
        # Check NaNs
        nan_pct = df.isna().mean()
        bad_cols = nan_pct[nan_pct > self.config["max_nan_pct"]].index.tolist()
        
        if bad_cols:
            issues.append(f"High NaN count in cols: {len(bad_cols)}")
            score -= (len(bad_cols) * 2) # Arbitrary penalty
            
        # Constant Columns
        constants = [col for col in df.columns if df[col].nunique() <= 1]
        if constants:
            issues.append(f"Constant columns found: {len(constants)}")
            score -= (len(constants) * 5)
            
        return {
            "valid": score > 70,
            "score": max(score, 0),
            "issues": issues,
            "metrics": {
                "nan_columns": len(bad_cols),
                "constant_columns": len(constants),
                "total_columns": len(df.columns)
            }
        }
