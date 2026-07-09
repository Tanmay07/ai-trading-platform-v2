from typing import Dict, Any, List

class AICommittee:
    def vote_on_trade(self, recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simulates individual specialized agents voting on a trade.
        """
        return [
            {"agent": "Technical Director", "vote": "BUY", "confidence": 0.85},
            {"agent": "Macro Director", "vote": "BUY", "confidence": 0.70},
            {"agent": "Risk Director", "vote": "HOLD", "confidence": 0.50},
            {"agent": "Portfolio Director", "vote": "BUY", "confidence": 0.90},
            {"agent": "Compliance Director", "vote": "BUY", "confidence": 1.0}
        ]
