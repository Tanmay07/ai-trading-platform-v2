import logging
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class FeatureRegistry:
    """Tracks metadata and versions for all engineered features."""
    
    def __init__(self):
        # In production, this would be a Postgres table.
        # For MVP, keeping an in-memory dictionary.
        self._registry = {}
        
    def register_feature_group(self, group_name: str, features: List[str], version: str, description: str):
        self._registry[group_name] = {
            "features": features,
            "version": version,
            "description": description,
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Registered feature group: {group_name} v{version}")
        
    def get_registered_features(self) -> Dict:
        return self._registry
        
    def get_all_feature_columns(self) -> List[str]:
        cols = []
        for group in self._registry.values():
            cols.extend(group["features"])
        return list(set(cols))
