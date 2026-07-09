import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List

class BreakoutScoreWeights(BaseModel):
    multi_timeframe: float
    relative_strength: float
    breakout_patterns: float
    sector_rotation: float
    price_action: float
    vwap: float
    support_resistance: float

class RelativeStrength(BaseModel):
    periods: List[int]
    market_benchmark: str

class PatternThresholds(BaseModel):
    vcp_max_contraction_percent: float
    darvas_box_duration: int
    tight_consolidation_atr_multiplier: float

class TechnicalConfig(BaseModel):
    breakout_score_weights: BreakoutScoreWeights
    relative_strength: RelativeStrength
    pattern_thresholds: PatternThresholds

    @classmethod
    def load(cls, config_path: str = "config/technical.yaml") -> "TechnicalConfig":
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / config_path
        if not path.exists():
            raise FileNotFoundError(f"Technical config not found at {path}")
            
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            
        return cls(**data)

# Global singleton
technical_config = TechnicalConfig.load()
