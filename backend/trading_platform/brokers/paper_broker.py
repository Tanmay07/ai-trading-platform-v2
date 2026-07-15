from typing import Dict, Any, List
import uuid
import logging
from datetime import datetime
from trading_platform.brokers.base_broker import BaseBroker

logger = logging.getLogger(__name__)

class PaperBroker(BaseBroker):
    """
    Simulated broker for paper trading. 
    Orders are executed instantly (if market) against the last known price.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.initial_capital = config.get("initial_capital", 1000000.0)
        self.commission_bps = config.get("commission_bps", 20)
        
        # In-memory store for paper trading state (in a real app, backed by DB)
        self.available_margin = self.initial_capital
        self.utilized_margin = 0.0
        self.positions: Dict[str, Dict[str, Any]] = {} 
        self.orders: List[Dict[str, Any]] = []
        
    def authenticate(self) -> bool:
        logger.info("PaperBroker: Authenticated successfully.")
        return True
        
    def get_profile(self) -> Dict[str, Any]:
        return {
            "broker": "PAPER_TRADING",
            "account_id": "PAPER-12345",
            "status": "active"
        }
        
    def get_margins(self) -> Dict[str, float]:
        return {
            "available": self.available_margin,
            "utilized": self.utilized_margin
        }
        
    def get_positions(self) -> List[Dict[str, Any]]:
        return list(self.positions.values())
        
    def place_order(self, symbol: str, quantity: int, side: str, order_type: str = "MARKET", price: float = 0.0) -> Dict[str, Any]:
        """Simulates placing an order. Assumes immediate fill for MARKET orders."""
        order_id = str(uuid.uuid4())
        
        # Mock current market price (In a real paper trader, this would fetch from Market Data platform)
        # We will use the passed 'price' as the execution price for simplicity if > 0, otherwise default 100
        exec_price = price if price > 0 else 100.0
        
        cost = exec_price * quantity
        commission = cost * (self.commission_bps / 10000.0)
        total_cost = cost + commission if side == "BUY" else cost - commission
        
        if side == "BUY" and self.available_margin < total_cost:
            return {"order_id": order_id, "status": "REJECTED", "message": "Insufficient margin for paper trade."}
            
        # Execute immediately
        if side == "BUY":
            self.available_margin -= total_cost
            self.utilized_margin += cost
        else:
            self.available_margin += total_cost
            self.utilized_margin -= cost
            
        order_record = {
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "order_type": order_type,
            "price": exec_price,
            "status": "COMPLETED",
            "timestamp": datetime.now().isoformat(),
            "message": "Paper trade filled instantly."
        }
        self.orders.append(order_record)
        
        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = {"symbol": symbol, "quantity": 0, "avg_price": 0.0}
            
        current_pos = self.positions[symbol]
        if side == "BUY":
            new_qty = current_pos["quantity"] + quantity
            current_pos["avg_price"] = ((current_pos["avg_price"] * current_pos["quantity"]) + (exec_price * quantity)) / new_qty
            current_pos["quantity"] = new_qty
        else:
            current_pos["quantity"] -= quantity
            
        if current_pos["quantity"] == 0:
            del self.positions[symbol]
            
        return order_record
        
    def cancel_order(self, order_id: str) -> bool:
        """Paper orders fill instantly, so they cannot usually be cancelled unless they are LIMIT orders."""
        logger.info(f"PaperBroker: Cancel order requested for {order_id}. Ignored for MARKET.")
        return False
