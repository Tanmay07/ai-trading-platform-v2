import logging
from typing import Dict, Any, List

logger = logging.getLogger("VirtualPortfolio")

class VirtualPortfolio:
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.open_positions: Dict[str, Dict[str, Any]] = {}
        self.closed_positions: List[Dict[str, Any]] = []
        
    def get_portfolio_nav(self) -> float:
        """Calculate Net Asset Value (Cash + Market Value of open positions)."""
        market_value = sum(pos["shares"] * pos["current_price"] for pos in self.open_positions.values())
        return self.cash + market_value
        
    def get_summary(self) -> Dict[str, Any]:
        nav = self.get_portfolio_nav()
        total_return = ((nav - self.initial_capital) / self.initial_capital) * 100
        
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "nav": nav,
            "total_return_pct": total_return,
            "open_positions_count": len(self.open_positions),
            "closed_positions_count": len(self.closed_positions)
        }
        
    def add_position(self, symbol: str, entry_price: float, shares: float, context: Dict[str, Any]):
        cost = entry_price * shares
        if cost > self.cash:
            logger.warning(f"Insufficient cash to buy {shares} of {symbol}. Cash: {self.cash}, Required: {cost}")
            # In a real engine, we'd partially fill or reject. Here we just reject.
            return False
            
        self.cash -= cost
        self.open_positions[symbol] = {
            "symbol": symbol,
            "entry_price": entry_price,
            "current_price": entry_price,
            "shares": shares,
            "context": context,
            "status": "ACTIVE",
            "days_held": 0
        }
        return True
        
    def close_position(self, symbol: str, exit_price: float, reason: str):
        if symbol not in self.open_positions:
            return False
            
        pos = self.open_positions.pop(symbol)
        revenue = pos["shares"] * exit_price
        self.cash += revenue
        
        pnl = revenue - (pos["shares"] * pos["entry_price"])
        pos["exit_price"] = exit_price
        pos["exit_reason"] = reason
        pos["pnl"] = pnl
        pos["return_pct"] = (exit_price - pos["entry_price"]) / pos["entry_price"]
        pos["status"] = "CLOSED"
        
        self.closed_positions.append(pos)
        return True
        
    def update_market_prices(self, price_map: Dict[str, float]):
        for symbol, pos in self.open_positions.items():
            if symbol in price_map:
                pos["current_price"] = price_map[symbol]
                pos["days_held"] += 1
