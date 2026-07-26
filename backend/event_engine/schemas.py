from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from datetime import datetime

class BaseEvent(BaseModel):
    event_id: str
    type: str # CORPORATE, MARKET, TECHNICAL, PORTFOLIO, MACRO
    subtype: str # e.g., QUARTERLY_RESULTS, GOLDEN_CROSS, GAP_UP
    timestamp: datetime
    source: str
    
    # Context
    symbols: List[str] = []
    sectors: List[str] = []
    portfolios: List[int] = []
    
    # Intelligence payload
    payload: Dict[str, Any] = {}

class ScoredEvent(BaseEvent):
    impact_score: float # 0 to 100
    confidence: float # 0 to 100
    priority: str # CRITICAL, HIGH, MEDIUM, LOW, IGNORE
    expected_duration: str # SHORT_TERM, MEDIUM_TERM, LONG_TERM
    expected_direction: str # BULLISH, BEARISH, NEUTRAL
    
class EventCorrelation(BaseModel):
    correlation_id: str
    primary_event_id: str
    related_event_ids: List[str]
    narrative: str
    created_at: datetime
