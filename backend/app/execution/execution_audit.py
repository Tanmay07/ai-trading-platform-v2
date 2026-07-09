import json
from datetime import datetime
from typing import Dict, Any

class ExecutionAudit:
    def log_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Stores an immutable audit trail of API requests/responses.
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "payload": payload
        }
        # MVP: Print to console, in prod would be written to secure storage
        print(f"[AUDIT] {json.dumps(audit_entry)}")
