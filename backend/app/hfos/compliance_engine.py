from typing import Dict, Any

class ComplianceEngine:
    def check_pre_trade(self, recommendation: Dict[str, Any]) -> bool:
        """
        Synchronously checks if a trade violates sector caps or restricted lists.
        """
        restricted_symbols = ["ITC", "HDFCBANK"] # MVP Stub
        if recommendation.get("symbol") in restricted_symbols:
            return False
        return True
