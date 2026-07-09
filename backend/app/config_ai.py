import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict

class ConsensusThresholds(BaseModel):
    buy_confidence_min: int
    conflict_max: int

class AIConfig(BaseModel):
    agent_weights: Dict[str, float]
    regime_adjustments: Dict[str, Dict[str, float]]
    consensus_thresholds: ConsensusThresholds

def load_ai_config() -> AIConfig:
    config_path = Path(__file__).parent.parent / "config" / "ai.yaml"
    if not config_path.exists():
        return AIConfig(
            agent_weights={},
            regime_adjustments={},
            consensus_thresholds=ConsensusThresholds(buy_confidence_min=75, conflict_max=30)
        )
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return AIConfig(**data)

ai_config = load_ai_config()
