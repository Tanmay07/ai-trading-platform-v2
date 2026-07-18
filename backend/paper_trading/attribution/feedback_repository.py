import logging
import json
import os
from typing import Dict, Any
from datetime import datetime
import uuid

logger = logging.getLogger("FeedbackRepository")

class FeedbackRepository:
    """
    Saves structured datasets of closed trades to power the Adaptive Learning Engine (Phase F5).
    """
    def __init__(self, repo_dir: str = "data/feedback_repo/"):
        self.repo_dir = repo_dir
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir)
            
    def store_trade_feedback(self, closed_position: Dict[str, Any], attribution: Dict[str, Any]) -> str:
        record_id = str(uuid.uuid4())
        context = closed_position.get("context", {})
        
        feedback_record = {
            "record_id": record_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "symbol": closed_position["symbol"],
            "trade_outcome": {
                "return_pct": closed_position.get("return_pct", 0.0),
                "pnl": closed_position.get("pnl", 0.0),
                "days_held": closed_position.get("days_held", 0),
                "exit_reason": closed_position.get("exit_reason", "UNKNOWN"),
                "is_winner": closed_position.get("return_pct", 0.0) > 0
            },
            "market_conditions_at_entry": context.get("market_conditions", {}),
            "prediction": context.get("prediction", {}),
            "portfolio_context": context.get("portfolio", {}),
            "execution_details": context.get("execution", {}),
            "attribution": attribution
        }
        
        file_path = os.path.join(self.repo_dir, f"{record_id}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(feedback_record, f, indent=4)
            logger.info(f"Feedback record saved for {closed_position['symbol']}: {record_id}")
        except Exception as e:
            logger.error(f"Failed to write feedback record for {closed_position['symbol']}: {str(e)}")
            
        return record_id
