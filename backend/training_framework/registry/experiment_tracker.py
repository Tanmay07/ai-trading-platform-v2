import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("ExperimentTracker")

class ExperimentTracker:
    def __init__(self, registry_path: str = "data/models/experiment_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                return json.load(f)
        return {"experiments": []}
        
    def _save_registry(self):
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
    def log_experiment(self, experiment_data: Dict[str, Any]):
        """
        Persists experiment tracking data.
        """
        exp_id = f"EXP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        experiment_data["experiment_id"] = exp_id
        experiment_data["timestamp"] = datetime.utcnow().isoformat()
        
        self.registry["experiments"].append(experiment_data)
        self._save_registry()
        
        logger.info(f"Experiment {exp_id} saved to registry.")
        return exp_id
        
    def get_experiments(self) -> list:
        # Return sorted by timestamp desc
        return sorted(self.registry.get("experiments", []), key=lambda x: x.get("timestamp", ""), reverse=True)
