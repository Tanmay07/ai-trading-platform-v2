import math
from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PositionSizer:
    def calculate_position(
        self,
        entry_price: float,
        stop_loss: float,
        max_monetary_risk: float,
        max_capital_allocation: float,
        available_buying_power: float,
        portfolio_capital: float
    ) -> Dict[str, Any]:
        """
        Calculates position size bounded by risk and capital constraints.
        Returns whole shares only.
        """
        if entry_price <= stop_loss:
            logger.warning("Entry price must be strictly greater than stop loss for long positions.")
            return {"recommended_quantity": 0, "capital_required": 0, "portfolio_percent": 0, "risk_amount": 0}
            
        risk_per_share = entry_price - stop_loss
        quantity = max_monetary_risk / risk_per_share
        
        # Constrain by max capital allocation
        max_shares_allocation = max_capital_allocation / entry_price
        quantity = min(quantity, max_shares_allocation)
        
        # Constrain by available buying power
        max_shares_buying_power = available_buying_power / entry_price
        quantity = min(quantity, max_shares_buying_power)
        
        quantity = math.floor(quantity)
        
        capital_required = quantity * entry_price
        actual_risk = quantity * risk_per_share
        portfolio_percent = (capital_required / portfolio_capital) * 100 if portfolio_capital > 0 else 0
        
        return {
            "recommended_quantity": quantity,
            "capital_required": round(capital_required, 2),
            "portfolio_percent": round(portfolio_percent, 2),
            "risk_amount": round(actual_risk, 2)
        }
