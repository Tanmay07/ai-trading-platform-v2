from typing import Dict, Any

class StrategyRetirement:
    def flag_for_retirement(self, strategy_id: str, reason: str) -> Dict[str, Any]:
        """
        Flags a decaying strategy for human review to deprecate.
        """
        return {
            "strategy_id": strategy_id,
            "status": "PENDING_RETIREMENT",
            "reason": reason
        }
