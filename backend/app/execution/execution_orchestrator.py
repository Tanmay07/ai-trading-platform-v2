from typing import Dict, Any
from app.execution.execution_validator import ExecutionValidator
from app.execution.execution_manager import ExecutionManager
from app.execution.order_router import OrderRouter
from app.notifications.notification_manager import NotificationManager

class ExecutionOrchestrator:
    def __init__(self):
        self.validator = ExecutionValidator()
        self.manager = ExecutionManager()
        self.router = OrderRouter()
        self.notifier = NotificationManager()
        
    def process_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a validated recommendation from Portfolio Layer and attempts execution.
        """
        # Convert recommendation to order
        order = {
            "ticker": recommendation.get("Ticker"),
            "action": "BUY",
            "quantity": 100, # Mock calculated quantity
            "price": 500.0   # Mock current price
        }
        
        # 1. Validate
        funds = self.manager.get_funds()
        positions = self.manager.get_positions()
        
        val_res = self.validator.validate_order(order, positions, funds)
        if not val_res["valid"]:
            self.notifier.notify(f"Order Rejected: {val_res['reason']}")
            return {"status": "REJECTED", "reason": val_res["reason"]}
            
        # 2. Route
        routed_order = self.router.route_order(order)
        
        # 3. Execute
        exec_res = self.manager.execute_order(routed_order)
        
        # 4. Notify
        self.notifier.notify(f"Order Executed: {exec_res}")
        
        return exec_res
