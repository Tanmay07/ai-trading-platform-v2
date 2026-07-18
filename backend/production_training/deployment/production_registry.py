import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("ProductionRegistry")

class ProductionRegistry:
    def __init__(self, registry_path: str = "data/models/production_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                return json.load(f)
        return {"active_version": None, "history": []}
        
    def _save_registry(self):
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
    def register_model(self, model_metadata: Dict[str, Any]) -> str:
        """
        Registers a new model version in the history.
        Does NOT automatically promote it unless explicitly requested.
        """
        version = f"v{len(self.registry['history']) + 1}.0"
        model_metadata["version"] = version
        self.registry["history"].append(model_metadata)
        self._save_registry()
        logger.info(f"Registered new production candidate: {version}")
        return version
        
    def promote(self, version: str) -> bool:
        """
        Sets the active production model version.
        """
        exists = any(m["version"] == version for m in self.registry["history"])
        if not exists:
            logger.error(f"Cannot promote {version}: Not found in registry.")
            return False
            
        self.registry["active_version"] = version
        self._save_registry()
        logger.info(f"Promoted {version} to Active Production Model.")
        return True
        
    def get_active_model(self) -> Dict[str, Any]:
        """
        Returns the metadata for the active production model.
        """
        active_ver = self.registry.get("active_version")
        if not active_ver:
            return {}
            
        for m in self.registry["history"]:
            if m["version"] == active_ver:
                return m
        return {}
        
    def rollback(self) -> bool:
        """
        Rolls back to the previous version in history.
        """
        history = self.registry["history"]
        if len(history) < 2:
            logger.error("Cannot rollback: No previous history available.")
            return False
            
        active_ver = self.registry.get("active_version")
        
        # Find index of active
        idx = -1
        for i, m in enumerate(history):
            if m["version"] == active_ver:
                idx = i
                break
                
        if idx > 0:
            prev_ver = history[idx-1]["version"]
            return self.promote(prev_ver)
        else:
             logger.error("Already on earliest version or active version not found.")
             return False
