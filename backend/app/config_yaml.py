import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

class UniverseFilters(BaseModel):
    minimum_price: float = 10.0
    minimum_market_cap: float = 500.0
    minimum_average_volume: int = 100000
    minimum_relative_volume: float = 1.0
    minimum_delivery_percent: float = 0.3
    maximum_spread: float = 0.05

class RiskManagement(BaseModel):
    atr_multiplier: float = 2.0
    max_portfolio_risk_percent: float = 0.02
    max_position_allocation_percent: float = 0.1

class ConfidenceWeights(BaseModel):
    trend: float = 0.3
    volume: float = 0.2
    momentum: float = 0.3
    volatility: float = 0.2

class RewardRatios(BaseModel):
    target_1: float = 1.0
    target_2: float = 2.0
    target_3: float = 3.0

class RecommendationConfig(BaseModel):
    max_count: int = 10

class TradingConfig(BaseModel):
    universe_filters: UniverseFilters = Field(default_factory=UniverseFilters)
    risk_management: RiskManagement = Field(default_factory=RiskManagement)
    confidence_weights: ConfidenceWeights = Field(default_factory=ConfidenceWeights)
    reward_ratios: RewardRatios = Field(default_factory=RewardRatios)
    recommendation: RecommendationConfig = Field(default_factory=RecommendationConfig)


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
