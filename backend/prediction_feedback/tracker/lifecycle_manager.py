from sqlalchemy.orm import Session
from prediction_feedback.storage.models import PredictionRecord
import logging

logger = logging.getLogger(__name__)

class LifecycleManager:
    """Handles state transitions for a prediction record."""
    
    @staticmethod
    def activate_prediction(db: Session, record_id: int, entry_price: float, target_price: float, stop_loss: float) -> PredictionRecord:
        """Transitions a prediction from 'Generated' to 'Active' when executed or paper traded."""
        record = db.query(PredictionRecord).filter(PredictionRecord.id == record_id).first()
        if not record:
            return None
            
        record.state = "Active"
        record.entry_price = entry_price
        record.target_price = target_price
        record.stop_loss = stop_loss
        
        db.commit()
        db.refresh(record)
        logger.info(f"Activated prediction {record_id} for {record.symbol}")
        return record

    @staticmethod
    def complete_prediction(db: Session, record_id: int) -> PredictionRecord:
        """Transitions a prediction to 'Completed', ready for evaluation."""
        record = db.query(PredictionRecord).filter(PredictionRecord.id == record_id).first()
        if record:
            record.state = "Completed"
            db.commit()
            db.refresh(record)
        return record
