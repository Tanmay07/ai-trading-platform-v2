import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

class RewardWeights(BaseModel):
    profit: float
    sharpe: float
    drawdown_penalty: float
    holding_period_penalty: float
    calibration_bonus: float

class LearningSchedules(BaseModel):
    frequency: str
    min_experiences_required: int

class PolicyParameters(BaseModel):
    learning_rate: float
    discount_factor: float

class ExplorationSettings(BaseModel):
    epsilon_initial: float
    epsilon_decay: float
    epsilon_min: float

class ThresholdLimits(BaseModel):
    min_confidence_adjust: float
    max_confidence_adjust: float
    min_exposure_adjust: float
    max_exposure_adjust: float

class ReplaySettings(BaseModel):
    batch_size: int
    memory_size: int

class ExposureLimits(BaseModel):
    max_sector_exposure: float
    max_single_stock_exposure: float

class RLConfig(BaseModel):
    reward_weights: RewardWeights
    learning_schedules: LearningSchedules
    policy_parameters: PolicyParameters
    exploration: ExplorationSettings
    threshold_limits: ThresholdLimits
    replay_settings: ReplaySettings
    exposure_limits: ExposureLimits

def load_rl_config() -> RLConfig:
    config_path = Path(__file__).parent.parent / "config" / "reinforcement.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return RLConfig(**data)

rl_config = load_rl_config()
