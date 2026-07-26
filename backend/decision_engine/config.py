from pydantic_settings import BaseSettings

class DecisionEngineConfig(BaseSettings):
    # Core Weights (must sum to 1.0)
    WEIGHT_TECHNICAL: float = 0.30
    WEIGHT_VALUATION: float = 0.30
    WEIGHT_CONTEXT: float = 0.20
    WEIGHT_RISK: float = 0.20
    
    # Thresholds for categorizations (configurable)
    STRONG_BUY_THRESHOLD: float = 85.0
    BUY_THRESHOLD: float = 70.0
    ACCUMULATE_THRESHOLD: float = 60.0
    HOLD_THRESHOLD: float = 45.0
    SELL_THRESHOLD: float = 30.0
    EXIT_IMMEDIATELY_THRESHOLD: float = 15.0

    class Config:
        env_prefix = "IDIE_"

config = DecisionEngineConfig()
