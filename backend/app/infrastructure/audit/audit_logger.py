import json
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    def log_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any]):
        """
        Writes immutable logs for administrative/system actions.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details
        }
        # MVP: Print to console, prod writes to secure storage
        print(f"[ENTERPRISE_AUDIT] {json.dumps(entry)}")
