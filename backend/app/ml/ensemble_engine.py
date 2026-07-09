import pandas as pd
from typing import Dict, Any
from app.config_ml import ml_config

class EnsembleEngine:
    def __init__(self, models: Dict[str, Any]):
        """
        models: {"xgboost": model_obj, "lightgbm": model_obj, "random_forest": model_obj}
        """
        self.models = models
        self.weights = ml_config.ensemble_weights
        
    def predict_proba(self, X: pd.DataFrame) -> pd.Series:
        if X.empty:
            return pd.Series()
            
        final_probs = pd.Series(0.0, index=X.index)
        total_weight = 0.0
        
        for name, model in self.models.items():
            if name in self.weights:
                w = self.weights[name]
                # Some models might need feature alignment, assuming X is aligned
                try:
                    probs = model.predict_proba(X)[:, 1] # Probability of class 1 (Hit)
                    final_probs += (probs * w)
                    total_weight += w
                except Exception:
                    pass
                    
        if total_weight > 0:
            final_probs /= total_weight
            
        return final_probs
