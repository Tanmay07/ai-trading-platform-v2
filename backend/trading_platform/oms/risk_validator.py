import logging
import yaml
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RiskValidator:
    """
    Validates every order against risk constraints before execution.
    """
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "../../../config/trading.yaml")
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                self.limits = config.get("risk_limits", {})
        except Exception:
            self.limits = {
                "max_portfolio_allocation_per_trade": 0.05,
                "max_open_orders": 10
            }
            
    def validate_order(self, symbol: str, quantity: int, price: float, side: str, portfolio_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Returns {"valid": bool, "reason": str}"""
        if side == "SELL":
            # Just verify they own the stock to avoid short selling in cash market
            positions = {p["symbol"]: p["quantity"] for p in portfolio_summary.get("positions", [])}
            if symbol not in positions or positions[symbol] < quantity:
                return {"valid": False, "reason": f"Insufficient holding for {symbol} to sell {quantity} shares."}
            return {"valid": True, "reason": ""}
            
        # BUY order logic
        cost = quantity * price
        net_worth = portfolio_summary.get("net_worth", 0)
        available = portfolio_summary.get("margins", {}).get("available", 0)
        
        if cost > available:
            return {"valid": False, "reason": f"Insufficient margin. Required: {cost}, Available: {available}"}
            
        max_allocation = net_worth * self.limits.get("max_portfolio_allocation_per_trade", 0.05)
        if cost > max_allocation:
            return {"valid": False, "reason": f"Order exceeds max allocation ({max_allocation})"}
            
        return {"valid": True, "reason": ""}
