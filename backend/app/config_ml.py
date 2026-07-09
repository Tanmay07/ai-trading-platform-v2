import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

class ModelParameters(BaseModel):
    xgboost: Dict[str, Any]
    lightgbm: Dict[str, Any]
    random_forest: Dict[str, Any]
    logistic_regression: Dict[str, Any]

class TrainingSchedule(BaseModel):
    frequency: str
    auto_retrain_on_drift: bool

class DriftThresholds(BaseModel):
    psi_alert_level: float
    accuracy_drop_alert_level: float

class CalibrationSettings(BaseModel):
    method: str

class RetrainingTriggers(BaseModel):
    max_model_age_days: int
    accuracy_threshold: float

class FeatureStoreSettings(BaseModel):
    storage_path: str

class MLConfig(BaseModel):
    model_parameters: ModelParameters
    training_schedule: TrainingSchedule
    drift_thresholds: DriftThresholds
    ensemble_weights: Dict[str, float]
    calibration_settings: CalibrationSettings
    retraining_triggers: RetrainingTriggers
    feature_store_settings: FeatureStoreSettings

def load_ml_config() -> MLConfig:
    config_path = Path(__file__).parent.parent / "config" / "ml.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return MLConfig(**data)

ml_config = load_ml_config()
