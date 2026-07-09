import yaml
from pathlib import Path
from pydantic import BaseModel

class CostsConfig(BaseModel):
    brokerage_pct: float
    stt_pct: float
    exchange_txn_pct: float
    gst_pct: float
    sebi_pct: float
    stamp_duty_pct: float

class SlippageConfig(BaseModel):
    base_slippage_pct: float
    volatility_multiplier: float

class ValidationConfig(BaseModel):
    min_cagr: float
    max_drawdown: float
    min_win_rate: float
    min_monte_carlo_survival: float

class MonteCarloConfig(BaseModel):
    iterations: int

class WalkForwardConfig(BaseModel):
    train_window_days: int
    test_window_days: int

class CapacityConfig(BaseModel):
    max_adv_participation_pct: float

class BacktestingConfig(BaseModel):
    costs: CostsConfig
    slippage: SlippageConfig
    validation: ValidationConfig
    monte_carlo: MonteCarloConfig
    walk_forward: WalkForwardConfig
    capacity: CapacityConfig

def load_backtesting_config() -> BacktestingConfig:
    config_path = Path(__file__).parent.parent / "config" / "backtesting.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return BacktestingConfig(**data)

backtesting_config = load_backtesting_config()
