from typing import Dict, Any
from app.config_execution import execution_config

class ExecutionValidator:
    def validate_order(self, order: Dict[str, Any], current_positions: list, funds: float) -> Dict[str, Any]:
        """
        Pre-trade checks before hitting broker API.
        """
        if execution_config.risk_limits.kill_switch_active:
            return {"valid": False, "reason": "KILL_SWITCH_ACTIVE"}
            
        required_margin = order.get("quantity", 0) * order.get("price", 0)
        
        if required_margin > funds:
            return {"valid": False, "reason": "INSUFFICIENT_FUNDS"}
            
        if len(current_positions) >= execution_config.risk_limits.max_open_trades:
            return {"valid": False, "reason": "MAX_OPEN_TRADES_EXCEEDED"}
            
        return {"valid": True, "reason": ""}
