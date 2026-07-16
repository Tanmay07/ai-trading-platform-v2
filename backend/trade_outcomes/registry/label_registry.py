import json
import os
from datetime import datetime
from typing import Dict, Any, List

class LabelRegistry:
    """
    Persists label strategies, their metrics, and versions to a JSON registry.
    """
    def __init__(self, registry_path: str = "data/models/label_registry.json"):
        self.registry_path = registry_path
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        
    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"versions": []}
        
    def _save_registry(self, data: Dict[str, Any]):
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    def register_labels(self, metrics: Dict[str, Dict[str, Any]], config: Dict[str, Any]):
        """
        Saves a new comparison run into the registry.
        """
        registry = self._load_registry()
        
        version_id = f"LABEL-VER-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        entry = {
            "version_id": version_id,
            "timestamp": datetime.utcnow().isoformat(),
            "config": config,
            "metrics": metrics
        }
        
        registry["versions"].append(entry)
        self._save_registry(registry)
        return version_id
        
    def get_latest_version(self) -> Dict[str, Any]:
        registry = self._load_registry()
        if not registry["versions"]:
            return {}
        return registry["versions"][-1]
        
    def get_all_versions(self) -> List[Dict[str, Any]]:
        return self._load_registry().get("versions", [])
