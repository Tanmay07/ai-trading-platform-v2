import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict

class MarketScoreWeights(BaseModel):
    market_regime: float
    market_breadth: float
    macro: float
    fii_dii: float
    volatility: float
    liquidity: float
    global_markets: float

class MarketConfig(BaseModel):
    market_score_weights: MarketScoreWeights
    exposure_rules: Dict[str, float]

    @classmethod
    def load(cls, config_path: str = "config/market.yaml") -> "MarketConfig":
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / config_path
        if not path.exists():
            raise FileNotFoundError(f"Market config not found at {path}")
            
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            
        return cls(**data)

market_config = MarketConfig.load()
