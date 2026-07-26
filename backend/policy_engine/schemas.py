from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from datetime import datetime

class PolicyWeights(BaseModel):
    technical: float = 25.0
    valuation: float = 25.0
    context: float = 25.0
    risk: float = 25.0

class PolicyThresholds(BaseModel):
    strong_buy: float = 90.0
    buy: float = 80.0
    accumulate: float = 65.0
    hold: float = 50.0
    watch: float = 40.0
    trim: float = 30.0
    sell: float = 20.0
    
class MethodologyConfig(BaseModel):
    methodology: str
    params: Dict[str, Any] = {}

class PolicyVersionCreate(BaseModel):
    weights: PolicyWeights
    thresholds: PolicyThresholds
    target_logic: MethodologyConfig
    stop_loss_logic: MethodologyConfig
    sizing_rules: Dict[str, Any] = {}
    review_rules: Dict[str, Any] = {}
    market_regime_rules: Dict[str, Any] = {}

class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    investment_style: str
    benchmark: str = "NIFTY50"
    initial_version: PolicyVersionCreate

class PolicyVersionResponse(BaseModel):
    id: int
    version_number: int
    status: str
    weights: Dict[str, Any]
    thresholds: Dict[str, Any]
    target_logic: Dict[str, Any]
    stop_loss_logic: Dict[str, Any]
    
    class Config:
        from_attributes = True

class PolicyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    investment_style: str
    active_version_id: Optional[int]
    versions: List[PolicyVersionResponse] = []
    
    class Config:
        from_attributes = True
