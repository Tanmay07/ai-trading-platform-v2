import joblib
import json
from pathlib import Path
from datetime import datetime

class PolicyRegistry:
    def __init__(self):
        self.registry_dir = "./data/policy_registry"
        Path(self.registry_dir).mkdir(parents=True, exist_ok=True)

    def save_policy(self, policy_obj, metrics: dict):
        version = datetime.utcnow().strftime("v%Y%m%d%H%M%S")
        model_dir = Path(self.registry_dir) / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(policy_obj, model_dir / "policy.pkl")
        
        metadata = {
            "version": version,
            "saved_at": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        pointer_file = Path(self.registry_dir) / "active_version.txt"
        with open(pointer_file, "w") as f:
            f.write(version)
            
        return version
        
    def load_active_policy(self):
        pointer_file = Path(self.registry_dir) / "active_version.txt"
        if not pointer_file.exists():
            return None, None
            
        with open(pointer_file, "r") as f:
            version = f.read().strip()
            
        model_dir = Path(self.registry_dir) / version
        try:
            policy = joblib.load(model_dir / "policy.pkl")
            with open(model_dir / "metadata.json", "r") as f:
                metadata = json.load(f)
            return policy, metadata
        except Exception:
            return None, None
