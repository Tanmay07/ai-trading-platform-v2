import os
import joblib
import json
from pathlib import Path
from datetime import datetime

class ModelRegistry:
    def __init__(self):
        self.registry_dir = "./data/model_registry"
        Path(self.registry_dir).mkdir(parents=True, exist_ok=True)

    def save_model(self, model_name: str, model, metadata: dict):
        version = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        model_dir = Path(self.registry_dir) / model_name / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(model, model_dir / "model.pkl")
        
        # Save metadata
        metadata["version"] = version
        metadata["saved_at"] = datetime.utcnow().isoformat()
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        # Update active pointer
        pointer_file = Path(self.registry_dir) / model_name / "active_version.txt"
        with open(pointer_file, "w") as f:
            f.write(version)
            
        return version
        
    def load_active_model(self, model_name: str):
        pointer_file = Path(self.registry_dir) / model_name / "active_version.txt"
        if not pointer_file.exists():
            return None, None
            
        with open(pointer_file, "r") as f:
            version = f.read().strip()
            
        return self.load_model_version(model_name, version)
        
    def load_model_version(self, model_name: str, version: str):
        model_dir = Path(self.registry_dir) / model_name / version
        model_file = model_dir / "model.pkl"
        meta_file = model_dir / "metadata.json"
        
        if not model_file.exists() or not meta_file.exists():
            return None, None
            
        model = joblib.load(model_file)
        with open(meta_file, "r") as f:
            metadata = json.load(f)
            
        return model, metadata
        
    def rollback(self, model_name: str, version: str):
        pointer_file = Path(self.registry_dir) / model_name / "active_version.txt"
        with open(pointer_file, "w") as f:
            f.write(version)
