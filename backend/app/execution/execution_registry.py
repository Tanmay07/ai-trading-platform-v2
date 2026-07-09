from typing import Dict, Any

class ExecutionRegistry:
    def __init__(self):
        # In memory MVP for storing active execution state
        self.orders = {}
        self.positions = {}
        
    def register_order(self, order_id: str, order_data: Dict[str, Any]):
        self.orders[order_id] = order_data
        
    def get_order(self, order_id: str) -> Dict[str, Any]:
        return self.orders.get(order_id)
