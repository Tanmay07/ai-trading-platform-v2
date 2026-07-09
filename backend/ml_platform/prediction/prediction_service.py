import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

from ml_platform.feature_store.feature_store import FeatureStore
from ml_platform.registry.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Exposes models for real-time or batch inference.
    Fetches the latest features from the Feature Store and runs the production model.
    """
    
    def __init__(self, registry: ModelRegistry):
        self.feature_store = FeatureStore()
        self.registry = registry

    def predict_symbol(self, symbol: str, model_name: str = "breakout_5d_ensemble") -> Dict[str, Any]:
        """
        Generates a live prediction for a specific symbol using the production model.
        """
        # 1. Load active model
        model = self.registry.load_production_model(model_name)
        if not model:
            return {"status": "error", "message": f"No production model found for {model_name}"}

        # 2. Get latest features for the symbol
        # We don't force recompute here; we expect background tasks to keep the Feature Store updated.
        df_features = self.feature_store.get_features(symbol)
        if df_features.empty:
            return {"status": "error", "message": f"No features found for {symbol}"}
            
        # Get the very last row (the most recent day)
        latest_features = df_features.iloc[[-1]]
        
        # 3. Predict
        try:
            # Drop Target columns if they exist (they shouldn't be passed to predict)
            cols_to_drop = [c for c in latest_features.columns if c.startswith('Target_') or c == 'Symbol']
            X_pred = latest_features.drop(columns=cols_to_drop)
            
            # Make sure X_pred columns match what the model expects. 
            # In a real system, the model registry would store the expected feature schema.
            
            pred_class = int(model.predict(X_pred)[0])
            
            # Try predict_proba
            probabilities = {}
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_pred)[0]
                
                # Assuming classes: -2, -1, 0, 1, 2
                classes = getattr(model, "classes_", [-2, -1, 0, 1, 2])
                
                for cls, prob in zip(classes, probs):
                    if cls == 2: probabilities["Strong_Buy"] = float(prob)
                    elif cls == 1: probabilities["Buy"] = float(prob)
                    elif cls == 0: probabilities["Hold"] = float(prob)
                    elif cls == -1: probabilities["Sell"] = float(prob)
                    elif cls == -2: probabilities["Strong_Sell"] = float(prob)
                    elif len(classes) == 2:
                        # Binary fallback
                        if cls == 1: probabilities["Breakout_Prob"] = float(prob)
                        elif cls == 0: probabilities["No_Breakout_Prob"] = float(prob)

            return {
                "status": "success",
                "symbol": symbol,
                "model_name": model_name,
                "prediction": pred_class,
                "probabilities": probabilities,
                "timestamp": latest_features.index[0].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return {"status": "error", "message": str(e)}
