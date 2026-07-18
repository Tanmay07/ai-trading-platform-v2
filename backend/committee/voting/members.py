from typing import Dict, Any
from committee.voting.committee_member import CommitteeMember, CommitteeVote

class PredictionMember(CommitteeMember):
    @property
    def member_name(self) -> str:
        return "Prediction Service"
        
    def evaluate(self, trade_context: Dict[str, Any]) -> CommitteeVote:
        prediction_data = trade_context.get("prediction", {})
        tq = prediction_data.get("trade_quality", 0)
        conf = prediction_data.get("confidence", 0)
        
        if tq >= 80:
            return CommitteeVote(self.member_name, "APPROVE", conf, "Strong prediction metrics.")
        elif tq >= 60:
            return CommitteeVote(self.member_name, "REVIEW", conf, "Marginal trade quality.")
        else:
            return CommitteeVote(self.member_name, "REJECT", conf, "Poor AI prediction quality.")

class PortfolioMember(CommitteeMember):
    @property
    def member_name(self) -> str:
        return "Portfolio Intelligence"
        
    def evaluate(self, trade_context: Dict[str, Any]) -> CommitteeVote:
        portfolio_data = trade_context.get("portfolio", {})
        is_rejected = portfolio_data.get("is_rejected", False)
        reasons = portfolio_data.get("rejection_reasons", [])
        health = portfolio_data.get("portfolio_health", 50)
        
        if is_rejected:
            reason_str = ", ".join(reasons) if reasons else "Violated portfolio constraints."
            return CommitteeVote(self.member_name, "REJECT", 95, reason_str)
            
        return CommitteeVote(self.member_name, "APPROVE", health, "Improves portfolio diversification and respects limits.")

class ExecutionMember(CommitteeMember):
    @property
    def member_name(self) -> str:
        return "Execution Planning"
        
    def evaluate(self, trade_context: Dict[str, Any]) -> CommitteeVote:
        execution_data = trade_context.get("execution", {})
        rr = execution_data.get("risk_reward", 0.0)
        risk_status = execution_data.get("risk_status", "")
        
        if rr < 2.0 or "REJECT" in risk_status:
            return CommitteeVote(self.member_name, "REJECT", 90, f"Poor execution profile: RR={rr}, Status={risk_status}")
            
        if "SHRUNK" in risk_status:
            return CommitteeVote(self.member_name, "REVIEW", 80, f"Valid setup but required position shrinkage due to risk budget. RR={rr}")
            
        return CommitteeVote(self.member_name, "APPROVE", 85, f"Strong execution profile. RR={rr}")
