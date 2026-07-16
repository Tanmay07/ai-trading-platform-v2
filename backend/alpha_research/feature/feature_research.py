import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.inspection import permutation_importance
import logging

logger = logging.getLogger("FeatureResearch")

class FeatureResearch:
    @staticmethod
    def analyze_features(df: pd.DataFrame, config: dict) -> dict:
        """
        Trains a transient memory-only surrogate model to extract SHAP/Permutation
        feature importances against the Trade_Quality_Score.
        """
        # Identify feature columns (everything that's not metadata or outcomes)
        meta_cols = [
            'symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
            'sector', 'industry', 'market_cap_bucket', 'tradability_score',
            'Simulated_Entry_Price', 'Simulated_Exit_Price', 'MFE_Pct', 'MAE_Pct',
            'Days_To_Target', 'Days_To_Stop', 'Trade_Outcome', 'Trade_Quality_Score',
            'Trade_Quality_Category', 'Label_Baseline', 'Label_TradeSuccess', 'Label_Ranking',
            'Feature_Version', 'Label_Version', 'Trade_Engine_Version',
            'Dataset_Version', 'Feature_Generation_Timestamp', 'Simulated_Return_Pct',
            'Returns_1d', 'Target_Return_5d', 'Returns_5d'
        ]
        
        feature_cols = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]
        
        # We sample down to avoid OOM or long running times
        sample_size = min(config.get('max_samples', 50000), len(df))
        sample_df = df.sample(n=sample_size, random_state=42).dropna(subset=feature_cols + ['Trade_Quality_Score'])
        
        if len(sample_df) == 0:
            return {"error": "No valid data for feature research"}
            
        X = sample_df[feature_cols]
        y = sample_df['Trade_Quality_Score']
        
        logger.info(f"Training transient Surrogate Model on {len(X)} samples for {len(feature_cols)} features...")
        
        model = RandomForestRegressor(
            n_estimators=config.get('n_estimators', 50),
            max_depth=config.get('max_depth', 8),
            random_state=42,
            n_jobs=-1
        )
        model.fit(X, y)
        
        # 1. Random Forest Feature Importance (Proxy for SHAP/Tree explainer)
        importances = model.feature_importances_
        
        # 2. Permutation Importance (on a smaller subset)
        perm_sample = min(5000, len(X))
        X_perm = X.iloc[:perm_sample]
        y_perm = y.iloc[:perm_sample]
        perm_result = permutation_importance(model, X_perm, y_perm, n_repeats=3, random_state=42, n_jobs=-1)
        perm_importances = perm_result.importances_mean
        
        # 3. Mutual Information (non-linear relationship)
        mi_sample = min(5000, len(X))
        X_mi = X.iloc[:mi_sample]
        y_mi = y.iloc[:mi_sample]
        mi_scores = mutual_info_regression(X_mi, y_mi, random_state=42)
        
        results = []
        for i, col in enumerate(feature_cols):
            results.append({
                "Feature": col,
                "SHAP_Proxy_Importance": round(float(importances[i]), 4),
                "Permutation_Importance": round(float(perm_importances[i]), 4),
                "Mutual_Information": round(float(mi_scores[i]), 4)
            })
            
        results = sorted(results, key=lambda x: x["SHAP_Proxy_Importance"], reverse=True)
        
        # Classify features
        top_20_pct = int(len(results) * 0.2)
        bottom_20_pct = int(len(results) * 0.2)
        
        for i, res in enumerate(results):
            if i < top_20_pct:
                res["Classification"] = "Essential"
            elif i > len(results) - bottom_20_pct:
                res["Classification"] = "Weak/Remove"
            else:
                res["Classification"] = "Useful"
                
        return {
            "Feature_Rankings": results,
            "Essential_Features": [r["Feature"] for r in results if r["Classification"] == "Essential"],
            "Features_To_Remove": [r["Feature"] for r in results if r["Classification"] == "Weak/Remove"]
        }
