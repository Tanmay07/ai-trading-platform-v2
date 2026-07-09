from typing import Dict, Any
from app.hfos.investment_committee import InvestmentCommittee
from app.hfos.compliance_engine import ComplianceEngine
from app.hfos.capital_allocator import CapitalAllocator

class HFOSOrchestrator:
    def __init__(self):
        self.compliance = ComplianceEngine()
        self.committee = InvestmentCommittee()
        self.allocator = CapitalAllocator()
        
    def process_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        The master flow for a trade: Compliance -> AI Vote -> Allocation -> Execution.
        """
        # 1. Pre-Trade Compliance
        if not self.compliance.check_pre_trade(recommendation):
            return {"status": "BLOCKED", "reason": "Compliance Violation"}
            
        # 2. AI Investment Committee
        vote_result = self.committee.review_recommendation(recommendation)
        if vote_result["status"] == "REJECTED":
            return {"status": "REJECTED", "reason": "Failed Committee Vote"}
            
        # 3. Allocation (Mock successful pipeline)
        return {"status": "EXECUTED", "allocated_capital_pct": 0.05}
