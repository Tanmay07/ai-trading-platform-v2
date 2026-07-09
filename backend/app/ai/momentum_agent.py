from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class MomentumAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        rs = candidate_data.get("Relative_Strength", 1.0)
        macd = candidate_data.get("MACD", 0)
        macd_sig = candidate_data.get("MACD_Signal", 0)
        
        if rs > 1.05:
            score += 25
            reasons.append(f"+ High Relative Strength ({rs:.2f})")
        elif rs < 0.95:
            score -= 20
            reasons.append(f"- Weak Relative Strength ({rs:.2f})")
            
        if macd > macd_sig:
            score += 15
            reasons.append("+ MACD > Signal (Bullish Momentum)")
        else:
            score -= 15
            reasons.append("- MACD < Signal (Bearish Momentum)")
            
        # Optional ROC or Acceleration check
        accel = candidate_data.get("Trend_Accel", 0)
        if accel > 0:
            score += 10
            reasons.append("+ Positive trend acceleration")
            
        score = max(0.0, min(100.0, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 70:
            rec = "BUY"
            conf = 80.0
        elif score < 40:
            rec = "SELL"
            conf = 75.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="MomentumAgent")
