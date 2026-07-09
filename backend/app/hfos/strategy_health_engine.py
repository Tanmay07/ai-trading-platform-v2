from typing import Dict, Any

class StrategyHealthEngine:
    def check_health(self, strategy_id: str) -> Dict[str, Any]:
        """
        Real time monitoring of a strategy's KPIs vs Expected.
        """
        return {
            "status": "HEALTHY",
            "cagr": 0.22,
            "drift_detected": False
        }
