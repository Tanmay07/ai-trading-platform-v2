from typing import Dict, Any, List

class PositionMonitor:
    def check_exits(self, open_positions: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates all open positions against their stops and targets.
        Returns a list of exit signals.
        """
        exits = []
        for symbol, pos in open_positions.items():
            current_price = pos["current_price"]
            context = pos.get("context", {})
            execution = context.get("execution", {})
            
            stop_loss = execution.get("stop_loss", 0.0)
            target_1 = execution.get("target_1", 0.0)
            target_2 = execution.get("target_2", 0.0)
            holding_period = execution.get("holding_period", 10)
            
            if current_price <= stop_loss:
                exits.append({
                    "symbol": symbol,
                    "exit_price": current_price,
                    "reason": "STOP_LOSS"
                })
            elif target_2 > 0 and current_price >= target_2:
                exits.append({
                    "symbol": symbol,
                    "exit_price": current_price,
                    "reason": "TARGET_2_REACHED"
                })
            elif target_1 > 0 and current_price >= target_1 and pos.get("partial_taken") is not True:
                # In a real system we'd exit half. For simplicity of MVP, we just exit all if it hits target 1 if we don't support partials fully in the portfolio yet.
                # Or mark partial_taken = True
                exits.append({
                    "symbol": symbol,
                    "exit_price": current_price,
                    "reason": "TARGET_1_REACHED"
                })
            elif pos["days_held"] >= holding_period:
                exits.append({
                    "symbol": symbol,
                    "exit_price": current_price,
                    "reason": "TIME_EXIT"
                })
                
        return exits
