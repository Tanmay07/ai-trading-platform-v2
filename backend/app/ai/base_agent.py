from pydantic import BaseModel, Field
from typing import List, Dict, Any

class AgentResponse(BaseModel):
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)
    recommendation: str = Field(...) # BUY, HOLD, SELL
    reasons: List[str] = Field(default_factory=list)
    agent_name: str

class BaseAgent:
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        """
        Evaluate the candidate and return an AgentResponse.
        Should be implemented by all subclasses.
        """
        raise NotImplementedError
