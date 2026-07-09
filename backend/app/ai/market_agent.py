from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class MarketAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        market_score = candidate_data.get("market_score", 50)
        health = candidate_data.get("trading_environment", "Neutral")
        
        score = float(market_score)
        
        if score > 75:
            reasons.append(f"+ Excellent Market Health ({score})")
        elif score > 60:
            reasons.append(f"+ Good Market Health ({score})")
        elif score < 40:
            reasons.append(f"- Poor Market Health ({score})")
        else:
            reasons.append(f"- Neutral Market Health ({score})")
            
        if health == "Excellent":
            reasons.append("+ Risk-On Environment")
        elif health in ["Poor", "Terrible"]:
            reasons.append("- Risk-Off Environment")
            
        rec = "HOLD"
        conf = 50.0
        if score > 65:
            rec = "BUY"
            conf = 85.0
        elif score < 45:
            rec = "SELL"
            conf = 75.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="MarketAgent")
