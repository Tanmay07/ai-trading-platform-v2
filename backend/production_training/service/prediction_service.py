import logging
import joblib
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from production_training.deployment.production_registry import ProductionRegistry
from production_training.explainability.shap_explainer import SHAPExplainer

logger = logging.getLogger("PredictionService")

class PredictionService:
    """
    The abstraction layer between the Recommendation Engine and the ML models.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PredictionService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        self.registry = ProductionRegistry()
        self.active_version = None
        self.classifier_model = None
        self.regressor_model = None
        self.features = []
        self.metadata = {}
        self.explainer = None
        self.optimal_threshold = 0.5
        self._load_active_model()
        
    def _load_active_model(self):
        active = self.registry.get_active_model()
        if not active:
            logger.warning("No active production model found.")
            return
            
        version = active["version"]
        if version == self.active_version:
            return # Already loaded
            
        model_dir = Path(f"data/models/production/{version}")
        
        # Load Classifier (backward compat if named 'model.joblib')
        if (model_dir / "classifier.joblib").exists():
             self.classifier_model = joblib.load(model_dir / "classifier.joblib")
        elif (model_dir / "model.joblib").exists():
             self.classifier_model = joblib.load(model_dir / "model.joblib")
        else:
            logger.error(f"Classifier file missing at {model_dir}")
            return
            
        # Load Regressor (if available)
        if (model_dir / "regressor.joblib").exists():
             self.regressor_model = joblib.load(model_dir / "regressor.joblib")
        else:
             self.regressor_model = None
             
        feat_path = model_dir / "features.json"
        with open(feat_path, "r") as f:
            self.features = json.load(f)
            
        self.metadata = active
        self.active_version = version
        self.optimal_threshold = active.get("optimal_threshold", 0.5)
        
        # Initialize Explainer on Classifier
        self.explainer = SHAPExplainer(self.classifier_model, self.features)
        
        logger.info(f"PredictionService successfully loaded model {version}")
        
    def predict(self, raw_features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Standardized prediction contract containing both Classification and Regression.
        """
        self._load_active_model() # Hot reload if changed
        
        if self.classifier_model is None:
            raise RuntimeError("PredictionService has no active model loaded.")
            
        # Ensure only the required features are passed
        missing = [f for f in self.features if f not in raw_features_df.columns]
        if missing:
             for f in missing:
                 raw_features_df[f] = 0.0
                 
        X = raw_features_df[self.features]
        
        # Classify
        raw_prob = self.classifier_model.predict(X)[0] 
        calibrated_prob = min(raw_prob * 1.1, 0.99) # Mock calibration
        confidence = abs(calibrated_prob - 0.5) * 2
        
        # Regress
        if self.regressor_model:
             reg_score = self.regressor_model.predict(X)[0]
             # LightGBM regression can output beyond [0, 100], so clip it
             trade_quality = max(0, min(100, float(reg_score)))
        else:
             # Fallback to probability scaled
             trade_quality = calibrated_prob * 100
             
        # SHAP Explanation
        explanations = self.explainer.explain_prediction(X)
        
        return {
            "classification_probability": round(float(calibrated_prob), 4),
            "trade_quality_prediction": round(float(trade_quality), 1),
            "confidence": round(float(confidence), 4),
            "expected_holding_days": 3,
            "model_version": self.active_version,
            "feature_mode": self.metadata.get("feature_mode", "unknown"),
            "dataset_version": self.metadata.get("dataset_version", "unknown"),
            "optimal_threshold": self.optimal_threshold,
            "explanations": explanations
        }
