from typing import Generator, Tuple
import numpy as np
import pandas as pd
from .purged_timeseries_split import PurgedTimeSeriesSplit
import yaml
from pathlib import Path
import logging

logger = logging.getLogger("WalkForwardValidator")

class WalkForwardValidator:
    def __init__(self, config_path: str = "config/training_framework.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        if not self.config_path.exists():
            # Defaults
            return {
                "n_splits": 4,
                "prediction_horizon_days": 5,
                "embargo_days": 7
            }
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            return data.get("training_framework", {}).get("validation", {
                "n_splits": 4,
                "prediction_horizon_days": 5,
                "embargo_days": 7
            })
            
    def get_cv_generator(self) -> PurgedTimeSeriesSplit:
        """Returns the configured scikit-learn compatible CV generator."""
        n_splits = self.config.get("n_splits", 4)
        prediction_horizon_days = self.config.get("prediction_horizon_days", 5)
        embargo_days = self.config.get("embargo_days", 7)
        
        logger.info(f"Initializing Purged Walk-Forward CV (Splits: {n_splits}, Horizon: {prediction_horizon_days}d, Embargo: {embargo_days}d)")
        
        return PurgedTimeSeriesSplit(
            n_splits=n_splits,
            prediction_horizon_days=prediction_horizon_days,
            embargo_days=embargo_days
        )
