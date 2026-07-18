import logging
import json
import os
from typing import Dict, Any, List
from datetime import datetime
import uuid

logger = logging.getLogger("DecisionLogger")

class DecisionLogger:
    """
    Persists complete decision audit trails to a JSON store.
    """
    def __init__(self, audit_dir: str = "data/audit/"):
        self.audit_dir = audit_dir
        if not os.path.exists(self.audit_dir):
            os.makedirs(self.audit_dir)
            
    def log_decision(self, symbol: str, final_decision: str, score: float, votes: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        decision_id = str(uuid.uuid4())
        
        audit_record = {
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "symbol": symbol,
            "final_decision": final_decision,
            "committee_score": score,
            "votes": votes,
            "context_snapshot": context
        }
        
        file_path = os.path.join(self.audit_dir, f"{decision_id}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(audit_record, f, indent=4)
            logger.info(f"Audit record saved for {symbol}: {decision_id}")
        except Exception as e:
            logger.error(f"Failed to write audit record for {symbol}: {str(e)}")
            
        return decision_id
        
    def get_audit(self, decision_id: str) -> Dict[str, Any]:
        file_path = os.path.join(self.audit_dir, f"{decision_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}
