import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("StrategyRegistry")

class StrategyRegistry:
    """
    Manages the lifecycle and metadata of independent strategy plugins.
    """
    def __init__(self, registry_dir: str = "data/strategy_registry/"):
        self.registry_dir = registry_dir
        if not os.path.exists(self.registry_dir):
            os.makedirs(self.registry_dir)
            
    def register_strategy(self, strategy_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Registers or updates a strategy's metadata."""
        path = os.path.join(self.registry_dir, f"{strategy_id}.json")
        
        # Load existing if present to preserve history
        if os.path.exists(path):
            with open(path, "r") as f:
                strategy = json.load(f)
        else:
            strategy = {
                "strategy_id": strategy_id,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "lifecycle_state": "Experimental",
                "evaluations": [],
                "allocations": []
            }
            
        # Update metadata
        strategy.update(metadata)
        strategy["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        self._save(strategy_id, strategy)
        return strategy
        
    def get_strategy(self, strategy_id: str) -> Dict[str, Any]:
        path = os.path.join(self.registry_dir, f"{strategy_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None
        
    def update_evaluation(self, strategy_id: str, metrics: Dict[str, Any]):
        strategy = self.get_strategy(strategy_id)
        if strategy:
            metrics["timestamp"] = datetime.utcnow().isoformat() + "Z"
            strategy["evaluations"].append(metrics)
            # Update top-level metrics for quick access
            strategy["latest_metrics"] = metrics
            self._save(strategy_id, strategy)
            
    def promote_strategy(self, strategy_id: str, new_state: str):
        strategy = self.get_strategy(strategy_id)
        if strategy:
            strategy["lifecycle_state"] = new_state
            self._save(strategy_id, strategy)
            
    def list_all_strategies(self) -> List[Dict[str, Any]]:
        strategies = []
        for filename in os.listdir(self.registry_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.registry_dir, filename)
                try:
                    with open(path, "r") as f:
                        strategies.append(json.load(f))
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
        return strategies
        
    def _save(self, strategy_id: str, data: Dict[str, Any]):
        path = os.path.join(self.registry_dir, f"{strategy_id}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved Strategy to Registry: {strategy_id}")
