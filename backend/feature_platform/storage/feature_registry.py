import pandas as pd
import json
import os
from datetime import datetime

class FeatureRegistry:
    """
    Stage 11 & Stage 12: Feature Governance and Feature Scoring
    """
    def __init__(self, registry_path: str = "config/feature_registry.json"):
        self.registry_path = registry_path
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"features": {}}
        
    def _save_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=4)
            
    def compute_composite_score(self, metadata: dict) -> float:
        # Weighted score: Quality (30%), Predictive (40%), Stability (20%), Redundancy (10%)
        quality = metadata.get("quality_score", 0) * 0.30
        predictive = metadata.get("predictive_score", 0) * 0.40
        stability = metadata.get("stability_score", 0) * 0.20
        redundancy = metadata.get("redundancy_score", 100) * 0.10
        
        # Penalize for leakage
        if metadata.get("has_leakage", False):
            return 0
            
        return round(quality + predictive + stability + redundancy, 2)
        
    def determine_status(self, score: float, has_leakage: bool) -> str:
        if has_leakage or score < 40:
            return "Rejected"
        elif score >= 75:
            return "Production Ready"
        else:
            return "Experimental"
            
    def register_feature(self, feature_name: str, category: str, validation_results: dict):
        score = self.compute_composite_score(validation_results)
        status = self.determine_status(score, validation_results.get("has_leakage", False))
        
        self.registry["features"][feature_name] = {
            "feature_id": f"FEAT_{feature_name.upper()}",
            "name": feature_name,
            "category": category,
            "version": "1.0.0",
            "date_validated": datetime.now().isoformat(),
            "composite_score": score,
            "status": status,
            "validation_details": validation_results
        }
        self._save_registry()
        
    def get_approved_features(self) -> list:
        approved = []
        for feat, meta in self.registry["features"].items():
            if meta["status"] == "Production Ready":
                approved.append(feat)
        return approved
