import yaml
from pathlib import Path
import logging

logger = logging.getLogger("ParameterSpace")

class ParameterSpace:
    def __init__(self, config_path: str = "config/training_framework.yaml"):
        self.config_path = Path(config_path)
        self.space = self._load_config()
        
    def _load_config(self) -> dict:
        default_space = {
            "learning_rate": [0.01, 0.03, 0.05, 0.1],
            "num_leaves": [31, 63, 127],
            "max_depth": [5, 8, 10, 12],
            "feature_fraction": [0.6, 0.7, 0.8, 0.9],
            "bagging_fraction": [0.6, 0.7, 0.8, 0.9],
            "bagging_freq": [1, 3, 5],
            "min_child_samples": [20, 50, 100],
            "lambda_l1": [0, 0.1, 1],
            "lambda_l2": [0, 0.1, 1],
            "n_estimators": [200, 400, 600, 800]
        }
        
        if not self.config_path.exists():
            return default_space
            
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("training_framework", {}).get("optimization", {}).get("hyperparameter_space", default_space)
            
    def get_space(self) -> dict:
        return self.space
