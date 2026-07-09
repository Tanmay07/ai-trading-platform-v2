import os
import joblib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Stores and retrieves trained models and their metadata."""
    
    def __init__(self, base_path: str = "data/model_registry"):
        self.base_path = Path(base_path)
        self.models_path = self.base_path / "models"
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # In a real system, metadata goes to a DB like Postgres/MLflow.
        # Here we'll use a simple in-memory dict for MVP.
        self._metadata_db = {}
        
    def save_model(self, model: Any, name: str, version: str, metrics: Dict[str, float]) -> bool:
        """Saves a model to disk and logs its metadata."""
        filename = f"{name}_v{version}.joblib"
        file_path = self.models_path / filename
        
        try:
            joblib.dump(model, file_path)
            
            # Record metadata
            self._metadata_db[f"{name}_v{version}"] = {
                "name": name,
                "version": version,
                "metrics": metrics,
                "created_at": datetime.now().isoformat(),
                "path": str(file_path),
                "status": "STAGING" # STAGING, PRODUCTION, ARCHIVED
            }
            logger.info(f"Successfully saved model {name} v{version} to registry.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model to registry: {e}")
            return False
            
    def promote_model(self, name: str, version: str) -> bool:
        """Promotes a model to PRODUCTION status."""
        key = f"{name}_v{version}"
        if key in self._metadata_db:
            # Demote others
            for k, meta in self._metadata_db.items():
                if meta["name"] == name and meta["status"] == "PRODUCTION":
                    meta["status"] = "ARCHIVED"
            
            self._metadata_db[key]["status"] = "PRODUCTION"
            logger.info(f"Promoted {name} v{version} to PRODUCTION.")
            return True
        return False
        
    def load_production_model(self, name: str) -> Optional[Any]:
        """Loads the currently active production model."""
        prod_meta = None
        for meta in self._metadata_db.values():
            if meta["name"] == name and meta["status"] == "PRODUCTION":
                prod_meta = meta
                break
                
        if not prod_meta:
            logger.warning(f"No PRODUCTION model found for {name}.")
            return None
            
        try:
            model = joblib.load(prod_meta["path"])
            logger.info(f"Loaded production model {name} v{prod_meta['version']}")
            return model
        except Exception as e:
            logger.error(f"Failed to load production model {name}: {e}")
            return None
            
    def get_registry_status(self) -> Dict[str, Any]:
        return self._metadata_db
