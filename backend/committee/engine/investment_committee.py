import yaml
import logging
from typing import Dict, Any, List

from committee.voting.members import PredictionMember, PortfolioMember, ExecutionMember
from committee.rules.rule_engine import RuleEngine
from committee.audit.decision_logger import DecisionLogger

logger = logging.getLogger("InvestmentCommittee")

class InvestmentCommittee:
    def __init__(self):
        with open("config/committee_rules.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        # Discover and register plugins (Hardcoded initialization for now, but design is plugin-ready)
        self.members = [
            PredictionMember(),
            PortfolioMember(),
            ExecutionMember()
        ]
        
        self.rule_engine = RuleEngine(self.config)
        self.audit_logger = DecisionLogger()
        
    def evaluate_trade(self, trade_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates the committee decision-making process.
        trade_context must contain "prediction", "portfolio", and "execution" dictionaries.
        """
        symbol = trade_context.get("symbol", "UNKNOWN")
        logger.info(f"Committee convened to evaluate trade for {symbol}")
        
        # 1. Hard Rule Veto Validation
        vetos = self.rule_engine.validate(trade_context)
        if vetos:
            final_decision = "REJECT"
            reason_str = " | ".join(vetos)
            decision_id = self.audit_logger.log_decision(symbol, final_decision, 0.0, [], trade_context)
            return self._build_response(symbol, final_decision, 0.0, [], reason_str, decision_id)
            
        # 2. Collect Votes from all Members
        votes = []
        for member in self.members:
            vote = member.evaluate(trade_context)
            votes.append(vote)
            
        # 3. Calculate Weighted Committee Score
        score, avg_conf = self._calculate_score(votes)
        
        # 4. Determine Final Decision based on configured thresholds
        final_decision = "BUY"
        if score < self.config["committee"]["approval_threshold"]:
            final_decision = "REVIEW"
        if score < self.config["committee"]["review_threshold"]:
            final_decision = "REJECT"
            
        # 5. Check for conflicting votes
        conflict_msg = ""
        approve_count = sum(1 for v in votes if v.vote == "APPROVE")
        reject_count = sum(1 for v in votes if v.vote == "REJECT")
        if approve_count > 0 and reject_count > 0:
            final_decision = "REVIEW" # Downgrade to manual review on internal conflict
            conflict_msg = "Internal committee conflict triggered manual REVIEW downgrade."
            
        # 6. Generate Explanation
        explanation = conflict_msg + "\n" + "\n".join([f"{v.member_name}: {v.reason}" for v in votes])
        
        # 7. Audit
        decision_id = self.audit_logger.log_decision(symbol, final_decision, score, [v.to_dict() for v in votes], trade_context)
        
        return self._build_response(symbol, final_decision, score, [v.to_dict() for v in votes], explanation, decision_id)
        
    def _calculate_score(self, votes: List[Any]) -> tuple[float, float]:
        weight_map = self.config.get("weights", {})
        
        # Default fallback weights if config keys mismatch member names
        member_weight_keys = {
            "Prediction Service": "prediction",
            "Portfolio Intelligence": "portfolio",
            "Execution Planning": "execution"
        }
        
        total_score = 0.0
        total_conf = 0.0
        total_weight = 0.0
        
        for v in votes:
            w_key = member_weight_keys.get(v.member_name, "")
            weight = weight_map.get(w_key, 0.33)
            
            # Map categorical vote to points
            if v.vote == "APPROVE":
                pts = 100
            elif v.vote == "REVIEW":
                pts = 50
            else:
                pts = 0
                
            total_score += (pts * weight)
            total_conf += (v.confidence * weight)
            total_weight += weight
            
        if total_weight > 0:
            return round(total_score / total_weight, 2), round(total_conf / total_weight, 2)
        return 0.0, 0.0
        
    def _build_response(self, symbol: str, final_decision: str, score: float, votes: List[Dict[str, Any]], explanation: str, decision_id: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "final_decision": final_decision,
            "committee_score": score,
            "votes": votes,
            "explanation": explanation,
            "decision_id": decision_id
        }
