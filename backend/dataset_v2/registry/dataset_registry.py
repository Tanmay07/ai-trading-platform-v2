import json
import os
import datetime
import logging

logger = logging.getLogger("DatasetRegistry")

class DatasetRegistry:
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self._ensure_registry()
        
    def _ensure_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, "w") as f:
                json.dump({"datasets": []}, f)
                
    def register_dataset(self, version_id: str, metadata: dict):
        with open(self.registry_path, "r") as f:
            data = json.load(f)
            
        record = {
            "version_id": version_id,
            "created_at": datetime.datetime.utcnow().isoformat(),
            **metadata
        }
        
        data["datasets"].append(record)
        
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=4)
            
        logger.info(f"Registered Dataset {version_id} in registry.")
        return version_id
        
    def get_latest_dataset(self):
        with open(self.registry_path, "r") as f:
            data = json.load(f)
        if not data["datasets"]:
            return None
        return data["datasets"][-1]
        
    def get_all_datasets(self):
        with open(self.registry_path, "r") as f:
            return json.load(f)["datasets"]
