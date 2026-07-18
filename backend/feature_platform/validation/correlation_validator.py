import pandas as pd
import numpy as np

class CorrelationValidator:
    """
    Stage 7 & 8: Correlation Analysis & Redundancy Detection
    Operates on the entire dataframe at once, rather than feature by feature.
    """
    def __init__(self, corr_threshold: float = 0.95):
        self.corr_threshold = corr_threshold
        
    def validate_features(self, df: pd.DataFrame, feature_cols: list) -> dict:
        """
        Returns a dict mapping feature_col -> validation_result
        """
        available_cols = [c for c in feature_cols if c in df.columns]
        if not available_cols:
            return {}
            
        # Compute Spearman correlation matrix (more robust to non-linear relationships)
        # using pandas corr for efficiency
        corr_matrix = df[available_cols].corr(method='spearman').abs()
        
        results = {}
        redundant_groups = []
        
        # Upper triangle mask
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        for col in available_cols:
            results[col] = {
                "valid": True, # Correlation doesn't strictly invalidate, but flags for redundancy
                "redundancy_score": 100,
                "issues": [],
                "highly_correlated_with": []
            }
            
        # Find features with correlation > threshold
        for col in upper.columns:
            high_corr = upper[col][upper[col] > self.corr_threshold]
            if not high_corr.empty:
                correlated_features = high_corr.index.tolist()
                results[col]["redundancy_score"] = max(0, 100 - (len(correlated_features) * 30))
                results[col]["issues"].append(f"Highly correlated with: {', '.join(correlated_features)}")
                results[col]["highly_correlated_with"] = correlated_features
                
                # We could mark the feature as invalid if we strictly want to drop redundancies,
                # but often we let models (like LightGBM) handle collinearity or let the Feature Registry
                # score penalize it.
                
        return results
