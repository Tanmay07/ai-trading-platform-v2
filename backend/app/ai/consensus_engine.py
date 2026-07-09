from typing import List, Dict, Any
from app.ai.base_agent import AgentResponse
from pydantic import BaseModel

class ConsensusResult(BaseModel):
    final_score: float
    agreement_percent: float
    conflict_score: float
    dominant_recommendation: str
    weighted_confidence: float

class ConsensusEngine:
    def calculate(self, responses: List[AgentResponse], weights: Dict[str, float]) -> ConsensusResult:
        total_score = 0.0
        total_weight = 0.0
        total_confidence = 0.0
        
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        
        for r in responses:
            w = weights.get(r.agent_name, 0.0)
            total_score += r.score * w
            total_confidence += r.confidence * w
            total_weight += w
            
            if r.recommendation == "BUY":
                buy_votes += w
            elif r.recommendation == "SELL":
                sell_votes += w
            else:
                hold_votes += w
                
        # Normalize in case weights don't sum exactly to 1.0
        if total_weight > 0:
            final_score = total_score / total_weight
            weighted_confidence = total_confidence / total_weight
        else:
            final_score = 50.0
            weighted_confidence = 50.0
            
        # Determine dominant recommendation based on weight
        if buy_votes >= sell_votes and buy_votes >= hold_votes:
            dominant = "BUY"
            agreement = buy_votes / total_weight if total_weight > 0 else 0
        elif sell_votes > buy_votes and sell_votes >= hold_votes:
            dominant = "SELL"
            agreement = sell_votes / total_weight if total_weight > 0 else 0
        else:
            dominant = "HOLD"
            agreement = hold_votes / total_weight if total_weight > 0 else 0
            
        # Conflict is basically how strong the opposition is to the dominant view
        conflict_score = (1.0 - agreement) * 100.0
        agreement_percent = agreement * 100.0
        
        return ConsensusResult(
            final_score=round(final_score, 2),
            agreement_percent=round(agreement_percent, 2),
            conflict_score=round(conflict_score, 2),
            dominant_recommendation=dominant,
            weighted_confidence=round(weighted_confidence, 2)
        )
