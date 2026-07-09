from typing import Dict, Any
from app.execution.broker_factory import BrokerFactory
from app.config_execution import execution_config
from app.execution.execution_audit import ExecutionAudit

class ExecutionManager:
    def __init__(self):
        self.broker = BrokerFactory.get_broker(execution_config.execution.active_broker)
        self.audit = ExecutionAudit()
        # Login on init
        self.broker.login()
        
    def execute_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes order to the active broker and audits the request.
        """
        self.audit.log_event("ORDER_PLACED", order)
        response = self.broker.place_order(order)
        self.audit.log_event("ORDER_RESPONSE", response)
        return response
        
    def get_funds(self) -> float:
        return self.broker.get_funds()
        
    def get_positions(self) -> list:
        return self.broker.get_positions()
