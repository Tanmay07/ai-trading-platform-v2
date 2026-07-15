import pandas as pd
import numpy as np
from typing import Dict, Any, List
import lightgbm as lgb

class FeatureDiagnostics:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def generate_feature_ranking(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Ranks top 50 features based on Split Gain (from LightGBM natively).
        Also calculates correlation with the target and basic stability metrics.
        """
        model = self.analyzer.model
        features = self.analyzer.features
        
        # Get feature importances (gain)
        importances = model.feature_importance(importance_type="gain")
        
        # Determine actual label
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        ranking = []
        for i, feat in enumerate(features):
            # Calculate Correlation with Target
            if feat in df.columns:
                corr = df[feat].corr(actual)
                if pd.isna(corr):
                    corr = 0.0
                
                # Stability (Standard Deviation / Mean) to measure if it's wildly swinging
                mean_val = df[feat].mean()
                std_val = df[feat].std()
                stability = (std_val / abs(mean_val)) if mean_val != 0 else 0
            else:
                corr = 0.0
                stability = 0.0
                
            ranking.append({
                "feature": feat,
                "information_gain": float(importances[i]),
                "correlation": round(float(corr), 4),
                "stability": round(float(stability), 4)
            })
            
        # Sort by gain
        ranking.sort(key=lambda x: x["information_gain"], reverse=True)
        
        top_k = self.config.get("top_features_to_rank", 50)
        return ranking[:top_k]
