import logging
from typing import Dict, Any, List
from trading_platform.brokers.broker_factory import BrokerFactory

logger = logging.getLogger(__name__)

class PositionManager:
    """
    Tracks portfolio PnL and manages open positions.
    Reconciles with the active broker.
    """
    def __init__(self):
        self.broker = BrokerFactory.get_broker()
        
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Calculates total PnL and retrieves margin details."""
        margins = self.broker.get_margins()
        positions = self.broker.get_positions()
        
        total_pnl = 0.0
        total_investment = 0.0
        
        for pos in positions:
            # PnL = (Current Price - Avg Price) * Quantity
            # Mock current price since we don't have a live feed injected here yet
            mock_current_price = pos.get("avg_price", 100.0) * 1.05 # Simulate 5% profit
            pnl = (mock_current_price - pos.get("avg_price", 0)) * pos.get("quantity", 0)
            
            total_pnl += pnl
            total_investment += (pos.get("avg_price", 0) * pos.get("quantity", 0))
            
            pos["current_price"] = mock_current_price
            pos["pnl"] = pnl
            
        return {
            "margins": margins,
            "positions": positions,
            "total_investment": total_investment,
            "total_pnl": total_pnl,
            "net_worth": margins.get("available", 0) + margins.get("utilized", 0) + total_pnl
        }
