from typing import Dict, Any
from app.execution.execution_registry import ExecutionRegistry

class OrderManager:
    def __init__(self):
        self.registry = ExecutionRegistry()
        
    def update_order_status(self, order_id: str, new_status: str):
        """
        State machine for order lifecycle (Pending -> Filled).
        """
        order = self.registry.get_order(order_id)
        if order:
            order["status"] = new_status
            self.registry.register_order(order_id, order)
