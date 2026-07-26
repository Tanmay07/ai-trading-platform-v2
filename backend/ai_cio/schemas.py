from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    portfolio_id: int
    query: str
    context_window: int = 10 # past n messages

class ChatResponse(BaseModel):
    reply: str
    sources: List[str]
    suggested_actions: List[str]

class AgentQuery(BaseModel):
    query: str
    portfolio_context: Dict[str, Any]
    market_context: Dict[str, Any]

class MorningBriefingResponse(BaseModel):
    date: str
    portfolio_summary: str
    market_overview: str
    key_events: List[Dict[str, Any]]
    action_items: List[str]

class ScenarioRequest(BaseModel):
    portfolio_id: int
    scenario_type: str # MARKET_DROP, SECTOR_ROTATION, NEW_INVESTMENT
    parameters: Dict[str, Any]

class ScenarioResponse(BaseModel):
    scenario_description: str
    estimated_impact: float
    risk_changes: List[str]
    mitigation_strategy: str
