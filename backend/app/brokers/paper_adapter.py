import uuid
from typing import Dict, Any, List
from app.brokers.base_broker import BaseBroker

class PaperAdapter(BaseBroker):
    def __init__(self):
        self.funds = 100000.0
        self.positions = []
        
    def login(self) -> bool:
        return True
        
    def get_funds(self) -> float:
        return self.funds
        
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())
        return {
            "order_id": order_id,
            "status": "FILLED",
            "filled_qty": order.get("quantity", 1),
            "average_price": order.get("price", 100.0)
        }
        
    def cancel_order(self, order_id: str) -> bool:
        return True
        
    def get_positions(self) -> List[Dict[str, Any]]:
        return self.positions
