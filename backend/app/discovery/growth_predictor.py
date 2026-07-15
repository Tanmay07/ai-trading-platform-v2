"""
Growth Predictor (AI Prediction Engine)

Predicts the probability of a 5%+ return in the next 30 days using the LightGBM Production Model.
"""
import pandas as pd
from typing import Dict, Any, Optional
from app.utils.logger import get_logger
from model_training.registry.model_registry import ModelRegistry
from feature_platform.storage.feature_store import FeatureStore
from model_training.explainability.shap_analysis import SHAPAnalyzer
import os
import sys

# Ensure backend root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class GrowthPredictor:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.registry = ModelRegistry()
        self.feature_store = FeatureStore()
        
        # Load production model
        self.model, self.calibrator, self.feature_names, self.metadata = self.registry.get_production_model()
        if self.model:
            self.shap_analyzer = SHAPAnalyzer(self.model)
        else:
            self.shap_analyzer = None

    def predict_growth_probability(self, symbol: str, momentum_score: float = 0, fundamental_score: float = 0, sentiment_score: float = 0) -> Optional[Dict[str, Any]]:
        """
        Uses the active production ML model to predict breakout probability.
        """
        if not self.model:
            self.logger.warning(f"No production model found. Skipping prediction for {symbol}.")
            return None
            
        try:
            # 1. Load latest features
            path = self.feature_store._get_path(symbol)
            if not os.path.exists(path):
                self.logger.warning(f"No features found for {symbol} in store.")
                return None
                
            df = pd.read_parquet(path)
            if df.empty:
                return None
                
            # Get the most recent row (latest date)
            latest_features = df.iloc[[-1]]
            
            # 2. Filter exactly the features the model was trained on
            # Fill missing with 0 or NaN as appropriate. Let's use NaN so LightGBM handles it.
            for col in self.feature_names:
                if col not in latest_features.columns:
                    latest_features[col] = pd.NA
                    
            X = latest_features[self.feature_names]
            
            # 3. Predict
            raw_prob = self.model.predict(X, num_iteration=self.model.best_iteration)[0]
            cal_prob = self.calibrator.predict([raw_prob])[0]
            
            # 4. Generate SHAP explainability
            shap_vals, base_val = self.shap_analyzer.generate_shap_values(X)
            
            # Get top 3 driving features (highest positive SHAP)
            shap_dict = dict(zip(self.feature_names, shap_vals[0]))
            sorted_shap = sorted(shap_dict.items(), key=lambda x: x[1], reverse=True)
            top_drivers = sorted_shap[:3]
            
            reasons = []
            for feat, val in top_drivers:
                if val > 0:
                    reasons.append(f"Strong positive contribution from {feat} (+{round(val, 3)})")
                    
            prob_percent = min(100.0, max(0.0, cal_prob * 100))
            
            return {
                "probability": round(prob_percent, 2),
                "confidence": round(prob_percent * 0.9, 2), # proxy for confidence
                "expected_return": round((prob_percent / 100.0) * 8.0, 2),
                "reasons": reasons
            }
            
        except Exception as e:
            self.logger.error(f"Failed to predict growth for {symbol}: {e}")
            return None

