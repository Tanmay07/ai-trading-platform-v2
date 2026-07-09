from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class VolumeAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        rv = candidate_data.get("Relative_Volume", 1.0)
        
        if rv > 2.0:
            score += 30
            reasons.append(f"+ Massive Volume Expansion ({rv:.1f}x)")
        elif rv > 1.2:
            score += 15
            reasons.append(f"+ Healthy Volume Expansion ({rv:.1f}x)")
        elif rv < 0.8:
            score -= 15
            reasons.append(f"- Weak Volume ({rv:.1f}x)")
            
        obv_trend = candidate_data.get("OBV_Trend", "Flat")
        if obv_trend == "Up":
            score += 15
            reasons.append("+ OBV trending Up (Accumulation)")
        elif obv_trend == "Down":
            score -= 15
            reasons.append("- OBV trending Down (Distribution)")
            
        score = max(0.0, min(100.0, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 70:
            rec = "BUY"
            conf = 80.0
        elif score < 40:
            rec = "SELL"
            conf = 70.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="VolumeAgent")
