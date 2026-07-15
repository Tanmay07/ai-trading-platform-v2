import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
import lightgbm as lgb
import yaml
import logging

from model_training.registry.model_registry import ModelRegistry
from model_training.training.dataset_loader import DatasetLoader

logger = logging.getLogger("PredictionAnalyzer")

class PredictionAnalyzer:
    def __init__(self):
        self.registry = ModelRegistry()
        self.loader = DatasetLoader()
        self._load_config()
        self.model = None
        self.calibrator = None
        self.features = None
        self.metadata = None
        self.test_data = None
        
    def _load_config(self):
        config_path = Path("config/diagnostics.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)["research_lab"]["diagnostics"]
        else:
            self.config = {
                "thresholds_to_test": [55, 60, 65, 70, 75, 80],
                "future_return_targets": [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
                "top_errors_to_analyze": 100,
                "label_warning_threshold": 0.10,
                "calibration_warning_threshold": 0.15
            }

    def initialize(self):
        """Loads model, calibrator, and test data."""
        logger.info("Initializing PredictionAnalyzer...")
        
        # Load Model
        self.model, self.calibrator, self.features, self.metadata = self.registry.get_production_model()
        if not self.model:
            raise ValueError("No production model found.")
            
        # Load Dataset and extract Test split
        dataset = self.loader.load_dataset()
        # Ensure we have the target column
        # Wait, the target during training was "is_breakout". 
        # But for full analysis we need "Target_Return_5d" and "Target_Return_7d" and "Target_10d_Return".
        # They should be in the parquet file.
        
        # If 'is_breakout' was dropped, let's just create the split manually based on Date.
        # Ensure index is datetime
        dates = dataset.index.get_level_values('Date')
        test_mask = dates.year >= 2024
        
        test_df = dataset[test_mask].copy()
        
        # Keep features required for model
        if not all(f in test_df.columns for f in self.features):
            logger.warning("Some features missing in test set! Padding with 0.")
            for f in self.features:
                if f not in test_df.columns:
                    test_df[f] = 0.0
                    
        X_test = test_df[self.features]
        
        # Run inference
        raw_preds = self.model.predict(X_test)
        
        # Calibrate
        calibrated_probs = self.calibrator.predict_proba(raw_preds)
        
        test_df["raw_score"] = raw_preds
        test_df["predicted_probability"] = calibrated_probs * 100 # percentage 0-100
        
        self.test_data = test_df
        logger.info(f"Initialized with {len(self.test_data)} test samples.")
        
    def get_test_data(self) -> pd.DataFrame:
        if self.test_data is None:
            self.initialize()
        return self.test_data
