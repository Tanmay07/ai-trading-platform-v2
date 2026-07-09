import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List

class ExecutionSettings(BaseModel):
    active_broker: str
    mode: str

class RiskLimits(BaseModel):
    kill_switch_active: bool
    max_daily_loss_pct: float
    max_open_trades: int
    max_sector_exposure_pct: float
    max_stock_allocation_pct: float
    max_leverage: float

class MarketSettings(BaseModel):
    open_time: str
    close_time: str

class RetrySettings(BaseModel):
    max_retries: int
    retry_delay_seconds: int

class NotificationSettings(BaseModel):
    enabled: bool
    channels: List[str]

class ConfigExecution(BaseModel):
    execution: ExecutionSettings
    risk_limits: RiskLimits
    market: MarketSettings
    retry: RetrySettings
    notifications: NotificationSettings

def load_execution_config() -> ConfigExecution:
    config_path = Path(__file__).parent.parent / "config" / "execution.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing {config_path}")
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return ConfigExecution(**data)

execution_config = load_execution_config()
