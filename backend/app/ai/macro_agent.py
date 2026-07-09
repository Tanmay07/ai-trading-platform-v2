from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class MacroAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        macro_score = candidate_data.get("macro_score", 50)
        vix = candidate_data.get("current_vix", 15)
        
        score = float(macro_score)
        
        if score > 70:
            reasons.append("+ Favorable Global Macro")
        elif score < 40:
            reasons.append("- Unfavorable Global Macro")
            
        if vix > 22:
            reasons.append(f"- High Volatility (VIX: {vix})")
        elif vix < 14:
            reasons.append(f"+ Low Volatility (VIX: {vix})")
            
        rec = "HOLD"
        conf = 50.0
        if score > 65:
            rec = "BUY"
            conf = 70.0
        elif score < 40:
            rec = "SELL"
            conf = 75.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="MacroAgent")
