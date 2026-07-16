import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
import logging

logger = logging.getLogger("FactorValidator")

class FactorValidator:
    @staticmethod
    def validate_factors(df: pd.DataFrame) -> dict:
        factors = [
            "Trend_Factor", "Relative_Strength_Factor", "Breakout_Quality_Factor",
            "Volatility_Factor", "Liquidity_Factor", "Market_Breadth_Factor",
            "Regime_Factor", "Risk_Factor", "Momentum_Factor", "Institutional_Activity_Factor"
        ]
        
        # We need Trade_Quality_Score as target
        if 'Trade_Quality_Score' not in df.columns:
            return {"error": "Trade_Quality_Score not found"}
            
        sample_df = df.dropna(subset=factors + ['Trade_Quality_Score']).sample(n=min(50000, len(df)), random_state=42)
        X = sample_df[factors]
        y = sample_df['Trade_Quality_Score']
        
        logger.info("Training Validator Surrogate Model...")
        model = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42, n_jobs=-1)
        model.fit(X, y)
        
        importances = model.feature_importances_
        mi_scores = mutual_info_regression(X.iloc[:5000], y.iloc[:5000], random_state=42)
        
        results = []
        for i, factor in enumerate(factors):
            results.append({
                "Factor": factor,
                "SHAP_Proxy_Importance": round(float(importances[i]), 4),
                "Mutual_Information": round(float(mi_scores[i]), 4),
                "Average_Score": round(float(df[factor].mean()), 2)
            })
            
        results = sorted(results, key=lambda x: x["SHAP_Proxy_Importance"], reverse=True)
        
        return {
            "Total_Factors": len(factors),
            "Factor_Rankings": results,
            "Strongest_Factor": results[0]["Factor"] if results else None,
            "Weakest_Factor": results[-1]["Factor"] if results else None
        }
