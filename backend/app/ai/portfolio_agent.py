from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class PortfolioAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        # Checking constraints like sector concentration (assuming it's passed or mocked)
        sector_score = candidate_data.get("Sector_Rank", 50)
        
        if sector_score > 80:
            score += 20
            reasons.append("+ Leading Sector")
        elif sector_score < 40:
            score -= 20
            reasons.append("- Laggard Sector")
            
        score = max(0.0, min(100.0, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 65:
            rec = "BUY"
            conf = 70.0
        elif score < 40:
            rec = "SELL"
            conf = 70.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="PortfolioAgent")
