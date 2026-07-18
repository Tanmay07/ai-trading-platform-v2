import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("AlphaRegistry")

class AlphaRegistry:
    """
    The Alpha Marketplace backend.
    Stores and retrieves alpha signals and their lifecycle states.
    """
    def __init__(self, registry_dir: str = "data/alpha_marketplace/"):
        self.registry_dir = registry_dir
        if not os.path.exists(self.registry_dir):
            os.makedirs(self.registry_dir)
            
    def register_signal(self, name: str, source: str, author: str) -> Dict[str, Any]:
        signal_id = name.lower().replace(" ", "_")
        
        signal = {
            "signal_id": signal_id,
            "name": name,
            "source": source,
            "author": author,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "lifecycle_state": "Experimental",
            "evaluations": [],
            "alpha_score": None,
            "promotion_recommendation": None
        }
        
        self._save(signal_id, signal)
        return signal
        
    def get_signal(self, signal_id: str) -> Dict[str, Any]:
        path = os.path.join(self.registry_dir, f"{signal_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None
        
    def update_evaluation(self, signal_id: str, evaluation_data: Dict[str, Any]):
        signal = self.get_signal(signal_id)
        if signal:
            signal["evaluations"].append(evaluation_data)
            # Update top-level metrics for quick access
            if "alpha_score" in evaluation_data:
                signal["alpha_score"] = evaluation_data["alpha_score"]
            if "promotion_recommendation" in evaluation_data:
                signal["promotion_recommendation"] = evaluation_data["promotion_recommendation"]
                
            self._save(signal_id, signal)
            
    def promote_signal(self, signal_id: str, new_state: str):
        signal = self.get_signal(signal_id)
        if signal:
            signal["lifecycle_state"] = new_state
            signal["updated_at"] = datetime.utcnow().isoformat() + "Z"
            self._save(signal_id, signal)
            
    def list_all_signals(self) -> List[Dict[str, Any]]:
        signals = []
        for filename in os.listdir(self.registry_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.registry_dir, filename)
                try:
                    with open(path, "r") as f:
                        signals.append(json.load(f))
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
        return signals
        
    def _save(self, signal_id: str, data: Dict[str, Any]):
        path = os.path.join(self.registry_dir, f"{signal_id}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved Alpha Signal to Registry: {signal_id}")
