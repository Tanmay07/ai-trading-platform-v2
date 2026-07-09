from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class SentimentAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = candidate_data.get("Sentiment_Score", 50.0)
        reasons = []
        
        score = float(score)
        
        if score > 75:
            reasons.append("+ Highly Positive News Sentiment")
        elif score > 60:
            reasons.append("+ Positive News Sentiment")
        elif score < 40:
            reasons.append("- Negative News Sentiment")
            
        rec = "HOLD"
        conf = 50.0
        if score > 65:
            rec = "BUY"
            conf = 70.0
        elif score < 40:
            rec = "SELL"
            conf = 75.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="SentimentAgent")
