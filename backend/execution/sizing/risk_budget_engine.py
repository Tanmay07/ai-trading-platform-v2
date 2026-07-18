import logging
from typing import Dict, Any, List

logger = logging.getLogger("RiskBudgetEngine")

class RiskBudgetEngine:
    """
    Ensures that individual trade risk and overall portfolio risk stay within configured budgets.
    """
    def __init__(self, max_trade_risk: float = 0.01, max_portfolio_risk: float = 0.06):
        self.max_trade_risk = max_trade_risk
        self.max_portfolio_risk = max_portfolio_risk
        
    def validate_and_size(self, position: Dict[str, Any], entry_price: float, stop_loss: float, total_capital: float) -> Dict[str, Any]:
        """
        Adjusts capital allocation for a single position if the risk is too high.
        Risk is defined as the distance from entry to stop loss multiplied by position size.
        """
        if entry_price <= 0 or stop_loss >= entry_price:
             logger.warning(f"{position.get('symbol')} invalid entry/stop: {entry_price}/{stop_loss}")
             position['execution_capital'] = 0.0
             position['risk_status'] = "REJECTED_INVALID_STOP"
             return position
             
        risk_per_share = entry_price - stop_loss
        risk_pct = risk_per_share / entry_price
        
        target_capital = position.get("capital_allocated", 0.0)
        
        # Calculate proposed total risk dollar amount
        proposed_risk_dollars = target_capital * risk_pct
        max_allowed_risk_dollars = total_capital * self.max_trade_risk
        
        if proposed_risk_dollars > max_allowed_risk_dollars:
            # Shrink position size to fit the risk budget exactly
            safe_capital = max_allowed_risk_dollars / risk_pct
            logger.info(f"{position.get('symbol')} Risk exceeded! Shrinking capital from {target_capital} to {safe_capital}")
            position['execution_capital'] = safe_capital
            position['risk_status'] = "SHRUNK_DUE_TO_RISK"
        else:
            position['execution_capital'] = target_capital
            position['risk_status'] = "PASSED"
            
        position['risk_pct'] = risk_pct
        position['risk_dollars'] = position['execution_capital'] * risk_pct
        
        return position
        
    def validate_portfolio_budget(self, positions: List[Dict[str, Any]], total_capital: float) -> bool:
        """
        Calculates total risk across all proposed trades.
        """
        total_risk_dollars = sum(p.get("risk_dollars", 0.0) for p in positions)
        return (total_risk_dollars / total_capital) <= self.max_portfolio_risk
