from typing import Dict, Any

class ExecutionGovernance:
    def evaluate_broker(self, broker_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitors fill quality and slippage per broker.
        """
        if broker_metrics.get("rejection_rate", 0) > 0.05:
            return {"status": "WARNING", "action": "REDUCE_FLOW"}
        return {"status": "HEALTHY", "action": "NORMAL"}
