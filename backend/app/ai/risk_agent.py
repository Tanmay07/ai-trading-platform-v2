from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class RiskAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        # Risk ratio (Reward / Risk)
        entry = candidate_data.get("Recommended_Entry", 0)
        stop = candidate_data.get("Stop_Loss", 0)
        target = candidate_data.get("Target_Price", 0)
        
        if entry > stop and target > entry:
            risk = entry - stop
            reward = target - entry
            rr_ratio = reward / risk if risk > 0 else 0
            
            if rr_ratio >= 3.0:
                score += 30
                reasons.append(f"+ Excellent R:R ({rr_ratio:.1f}:1)")
            elif rr_ratio >= 2.0:
                score += 15
                reasons.append(f"+ Good R:R ({rr_ratio:.1f}:1)")
            elif rr_ratio < 1.5:
                score -= 20
                reasons.append(f"- Poor R:R ({rr_ratio:.1f}:1)")
                
        # Stop loss percentage
        if entry > 0 and stop > 0:
            sl_pct = (entry - stop) / entry
            if sl_pct > 0.08:
                score -= 10
                reasons.append(f"- Wide Stop Loss ({sl_pct*100:.1f}%)")
            elif sl_pct < 0.04:
                score += 10
                reasons.append(f"+ Tight Stop Loss ({sl_pct*100:.1f}%)")
                
        score = max(0.0, min(100.0, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 65:
            rec = "BUY"
            conf = 80.0
        elif score < 40:
            rec = "SELL"
            conf = 75.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="RiskAgent")
