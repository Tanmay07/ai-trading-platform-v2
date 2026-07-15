import json
import os
import joblib
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger("ModelRegistry")

class ModelRegistry:
    def __init__(self, models_dir: str = "data/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.models_dir / "registry.json"
        
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"models": []}

    def _save_registry(self):
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=4)

    def register_model(self, 
                       model, 
                       calibrator,
                       metadata: dict,
                       feature_names: list,
                       is_production: bool = True):
        """
        Saves the LightGBM model, calibrator, and metadata.
        """
        version = f"v{len(self.registry['models']) + 1}.0"
        timestamp = datetime.utcnow().isoformat()
        
        # Paths
        model_path = self.models_dir / f"lightgbm_{version}.txt"
        calibrator_path = self.models_dir / f"calibrator_{version}.joblib"
        features_path = self.models_dir / f"features_{version}.json"
        
        # Save model
        model.save_model(str(model_path))
        
        # Save calibrator
        joblib.dump(calibrator, calibrator_path)
        
        # Save feature names
        with open(features_path, 'w') as f:
            json.dump(feature_names, f)
            
        entry = {
            "version": version,
            "created_at": timestamp,
            "status": "production" if is_production else "archived",
            "model_path": str(model_path),
            "calibrator_path": str(calibrator_path),
            "features_path": str(features_path),
            "metadata": metadata
        }
        
        # Demote previous production model
        if is_production:
            for m in self.registry["models"]:
                if m["status"] == "production":
                    m["status"] = "archived"
                    
        self.registry["models"].append(entry)
        self._save_registry()
        
        logger.info(f"Successfully registered model {version} as Production.")
        return version

    def get_production_model(self):
        """Loads the current production model, calibrator, and features."""
        for m in self.registry["models"]:
            if m["status"] == "production":
                import lightgbm as lgb
                model = lgb.Booster(model_file=m["model_path"])
                calibrator = joblib.load(m["calibrator_path"])
                with open(m["features_path"], 'r') as f:
                    features = json.load(f)
                return model, calibrator, features, m
        return None, None, None, None
