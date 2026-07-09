from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class BreakoutAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        breakout_score = candidate_data.get("breakout_score", 50)
        vcp = candidate_data.get("VCP_Pattern", False)
        dist_res = candidate_data.get("Dist_to_Res", 100)
        
        score = float(breakout_score)
        reasons = []
        
        if score > 70:
            reasons.append("+ Strong Phase 2 Breakout Score")
        elif score < 40:
            reasons.append("- Weak Phase 2 Breakout Score")
            
        if vcp:
            score += 10
            reasons.append("+ VCP Pattern detected")
            
        if dist_res < 2:
            score += 10
            reasons.append("+ Very close to resistance breakout")
        elif dist_res < 5:
            score += 5
            reasons.append("+ Approaching resistance")
        else:
            score -= 5
            reasons.append("- Far from resistance")
            
        score = max(0.0, min(100.0, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 75:
            rec = "BUY"
            conf = 85.0
        elif score < 40:
            rec = "SELL"
            conf = 70.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="BreakoutAgent")
