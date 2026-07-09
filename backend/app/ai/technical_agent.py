from app.ai.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any

class TechnicalAgent(BaseAgent):
    async def evaluate(self, candidate_data: Dict[str, Any]) -> AgentResponse:
        score = 50.0
        reasons = []
        
        atr = candidate_data.get("ATR_14", 0)
        close = candidate_data.get("Close", 1)
        if (atr / close) < 0.05:
            score += 20
            reasons.append("+ Low volatility (ATR)")
        else:
            score -= 10
            reasons.append("- High volatility (ATR)")
            
        ema_20 = candidate_data.get("EMA_20", 0)
        ema_50 = candidate_data.get("EMA_50", 0)
        if ema_20 > ema_50:
            score += 20
            reasons.append("+ EMA 20 > EMA 50")
        else:
            score -= 20
            reasons.append("- EMA 20 < EMA 50")
            
        rsi = candidate_data.get("RSI_14", 50)
        if 40 <= rsi <= 70:
            score += 10
            reasons.append("+ RSI in sweet spot")
        elif rsi > 70:
            score -= 10
            reasons.append("- RSI Overbought")
        else:
            score -= 10
            reasons.append("- RSI Oversold")
            
        score = max(0, min(100, score))
        
        rec = "HOLD"
        conf = 50.0
        if score > 70:
            rec = "BUY"
            conf = 80.0
        elif score < 40:
            rec = "SELL"
            conf = 70.0
            
        return AgentResponse(score=score, confidence=conf, recommendation=rec, reasons=reasons, agent_name="TechnicalAgent")
