import pandas as pd
from typing import Dict, Any
from app.ml.model_registry import ModelRegistry
from app.ml.ensemble_engine import EnsembleEngine

class PredictionEngine:
    def __init__(self):
        self.registry = ModelRegistry()
        self.active_pack, self.metadata = self.registry.load_active_model("champion_ensemble")
        
        if self.active_pack:
            self.features = self.active_pack.get("features", [])
            self.ensemble = EnsembleEngine({
                "xgboost": self.active_pack.get("xgb"),
                "lightgbm": self.active_pack.get("lgb"),
                "random_forest": self.active_pack.get("rf")
            })
            self.meta = self.active_pack.get("meta")
            self.calibrator = self.active_pack.get("calibrator")
            self.is_ready = True
        else:
            self.is_ready = False

    def predict(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_ready:
            return {"buy_probability": 0.5, "calibration_error": 0.0, "model_version": "none"}
            
        # Extract features
        df = pd.DataFrame([candidate_data])
        
        # Ensure all required features are present
        for f in self.features:
            if f not in df.columns:
                df[f] = 0.0
                
        X = df[self.features]
        # Clean non-numeric data
        for col in X.columns:
             X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0.0)
                
        ensemble_prob = self.ensemble.predict_proba(X).iloc[0]
        
        # Meta layer
        consensus = candidate_data.get("consensus_score", 50)
        regime = 0 if candidate_data.get("regime") != "Strong Bull" else 1 # Simplify for now
        
        X_meta = pd.DataFrame({
            'ensemble_prob': [ensemble_prob],
            'consensus': [consensus],
            'regime': [regime]
        })
        
        meta_prob = self.meta.predict_proba(X_meta)
        
        calibrated_prob = self.calibrator.predict(meta_prob).iloc[0]
        
        return {
            "buy_probability": round(float(calibrated_prob), 4),
            "sell_probability": round(1.0 - float(calibrated_prob), 4),
            "hold_probability": 0.0, # Binary classification for now
            "ensemble_confidence": round(float(ensemble_prob), 4),
            "meta_learner_score": round(float(meta_prob.iloc[0]), 4),
            "calibration_error": self.metadata.get("calibration_error", 0.0) if self.metadata else 0.0,
            "model_version": self.metadata.get("version", "unknown") if self.metadata else "unknown",
            "top_features": self.features[:5]
        }
