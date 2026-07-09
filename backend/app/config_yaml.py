import yaml
from pathlib import Path
from pydantic import BaseModel

class UniverseFilters(BaseModel):
    minimum_price: float
    minimum_market_cap: float
    minimum_average_volume: int
    minimum_relative_volume: float
    minimum_delivery_percent: float
    maximum_spread: float

class RiskManagement(BaseModel):
    atr_multiplier: float
    max_portfolio_risk_percent: float
    max_position_allocation_percent: float

class ConfidenceWeights(BaseModel):
    trend: float
    volume: float
    momentum: float
    volatility: float

class RewardRatios(BaseModel):
    target_1: float
    target_2: float
    target_3: float

class RecommendationConfig(BaseModel):
    max_count: int

class TradingConfig(BaseModel):
    universe_filters: UniverseFilters
    risk_management: RiskManagement
    confidence_weights: ConfidenceWeights
    reward_ratios: RewardRatios
    recommendation: RecommendationConfig

    @classmethod
    def load(cls, config_path: str = "config/trading.yaml") -> "TradingConfig":
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / config_path
        if not path.exists():
            raise FileNotFoundError(f"Trading config not found at {path}")
            
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            
        return cls(**data)

# Global singleton
trading_config = TradingConfig.load()
