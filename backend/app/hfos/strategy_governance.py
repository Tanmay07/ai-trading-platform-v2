from typing import Dict, Any

class StrategyGovernance:
    def request_promotion(self, strategy_id: str) -> Dict[str, Any]:
        """
        Transitions state from Candidate -> Pending Approval.
        """
        return {"strategy_id": strategy_id, "status": "PENDING_APPROVAL"}
        
    def approve_promotion(self, strategy_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Human explicitly approves a strategy for production.
        """
        return {"strategy_id": strategy_id, "status": "PRODUCTION", "approved_by": admin_id}
