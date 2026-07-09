from sqlalchemy.orm import Session
from typing import Dict, Any
from prediction_feedback.storage.models import PredictionRecord
import logging

logger = logging.getLogger(__name__)

class PredictionTracker:
    """Tracks a new recommendation from the decision engine into the feedback database."""
    
    @staticmethod
    def track_prediction(db: Session, decision: Dict[str, Any]) -> PredictionRecord:
        """
        Takes the output of MetaDecisionEngine and stores it as a 'Generated' prediction.
        """
        record = PredictionRecord(
            symbol=decision.get("symbol"),
            action=decision.get("action"),
            confidence=decision.get("confidence"),
            final_score=decision.get("final_score"),
            regime=decision.get("regime"),
            explanation=decision.get("explanation"),
            state="Generated"
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        logger.info(f"Tracked new prediction for {record.symbol} (ID: {record.id})")
        return record
