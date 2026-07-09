import yaml
from pathlib import Path
from pydantic import BaseModel

class LimitsConfig(BaseModel):
    max_sector_exposure: float
    max_stock_allocation: float
    correlation_threshold: float

class KellyConfig(BaseModel):
    fraction_multiplier: float
    max_kelly_allocation: float

class RebalanceConfig(BaseModel):
    frequency: str
    drift_tolerance: float

class OptimizationConfig(BaseModel):
    method: str
    risk_free_rate: float

class StressTestConfig(BaseModel):
    market_crash: float
    volatility_spike: float

class PortfolioConfig(BaseModel):
    limits: LimitsConfig
    kelly: KellyConfig
    rebalance: RebalanceConfig
    optimization: OptimizationConfig
    stress_test: StressTestConfig

def load_portfolio_config() -> PortfolioConfig:
    config_path = Path(__file__).parent.parent / "config" / "portfolio.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return PortfolioConfig(**data)

portfolio_config = load_portfolio_config()
