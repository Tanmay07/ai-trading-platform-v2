import logging
from sklearn.model_selection import RandomizedSearchCV
from lightgbm import LGBMClassifier
import yaml
from pathlib import Path
import pandas as pd
import numpy as np

from training_framework.validation.walk_forward_split import WalkForwardValidator
from training_framework.optimization.parameter_space import ParameterSpace

logger = logging.getLogger("RandomizedSearch")

class RandomizedSearchOptimizer:
    def __init__(self, config_path: str = "config/training_framework.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.validator = WalkForwardValidator(config_path)
        self.param_space = ParameterSpace(config_path)
        
    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {"n_iter": 25, "scoring_metric": "roc_auc"}
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("training_framework", {}).get("optimization", {"n_iter": 25, "scoring_metric": "roc_auc"})
            
    def run_search(self, X: pd.DataFrame, y: pd.Series):
        """
        Executes RandomizedSearchCV over the provided dataset using Purged Walk Forward CV.
        The dataset provided should ONLY be the Training portion (e.g. 2019-2023).
        """
        logger.info(f"Initializing Randomized Search (Iterations: {self.config.get('n_iter', 25)})")
        
        cv_generator = self.validator.get_cv_generator()
        param_distributions = self.param_space.get_space()
        
        lgbm = LGBMClassifier(
            objective='binary',
            boosting_type='gbdt',
            verbosity=-1,
            random_state=42
        )
        
        search = RandomizedSearchCV(
            estimator=lgbm,
            param_distributions=param_distributions,
            n_iter=self.config.get("n_iter", 25),
            scoring=self.config.get("scoring_metric", "roc_auc"),
            cv=cv_generator,
            verbose=2,
            random_state=42,
            n_jobs=1,  # Keep at 1 to avoid multiprocessing issues with large memory footprints, unless specified
            return_train_score=True
        )
        
        logger.info("Starting Search. This may take a while...")
        search.fit(X, y)
        
        logger.info(f"Search completed. Best Score: {search.best_score_:.4f}")
        return search
