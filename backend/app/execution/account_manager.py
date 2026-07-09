from typing import Dict, Any
from app.execution.execution_manager import ExecutionManager

class AccountManager:
    def __init__(self):
        self.exec_manager = ExecutionManager()
        
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Returns unified account summary.
        """
        return {
            "funds": self.exec_manager.get_funds(),
            "status": "active"
        }
