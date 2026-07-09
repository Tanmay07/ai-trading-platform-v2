from typing import List, Dict, Any
from app.ai.base_agent import AgentResponse
from app.ai.consensus_engine import ConsensusResult
from app.config_ai import ai_config

class SupervisorAgent:
    def __init__(self):
        self.thresholds = ai_config.consensus_thresholds
        
    def finalize_decision(self, consensus: ConsensusResult, responses: List[AgentResponse], market_regime: str) -> Dict[str, Any]:
        """
        The Supervisor has the final say. It can ignore weak signals,
        reduce confidence during conflict, or force a HOLD.
        """
        final_rec = consensus.dominant_recommendation
        final_conf = consensus.weighted_confidence
        
        # Rule 1: High Conflict penalty
        if consensus.conflict_score > self.thresholds.conflict_max:
            final_conf *= 0.8
            if final_rec == "BUY":
                final_rec = "HOLD"  # Too much conflict to buy
                
        # Rule 2: Absolute minimum confidence for BUY
        if final_rec == "BUY" and final_conf < self.thresholds.buy_confidence_min:
            final_rec = "HOLD"
            
        # Rule 3: Hard Risk override in Bear markets
        if market_regime == "Bear":
            # Check what RiskAgent says
            risk_resp = next((r for r in responses if r.agent_name == "RiskAgent"), None)
            if risk_resp and risk_resp.recommendation == "SELL":
                final_rec = "SELL"
                final_conf = max(final_conf, 80.0) # Confident in selling
                
        return {
            "final_recommendation": final_rec,
            "final_confidence": round(final_conf, 2),
            "consensus_score": consensus.final_score,
            "agreement_percent": consensus.agreement_percent,
            "conflict_score": consensus.conflict_score
        }
