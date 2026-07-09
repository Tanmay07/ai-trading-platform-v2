from typing import Dict, Any

class AlphaDecayEngine:
    def monitor_decay(self, strategy_id: str, live_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects if a production strategy is losing edge.
        """
        if live_metrics.get("rolling_sharpe", 1.0) < 0.20:
            return {"status": "DECAYED", "recommendation": "RETIRE"}
        return {"status": "HEALTHY", "recommendation": "KEEP"}
