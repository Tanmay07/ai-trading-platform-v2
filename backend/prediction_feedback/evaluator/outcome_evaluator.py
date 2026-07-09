from sqlalchemy.orm import Session
from prediction_feedback.storage.models import PredictionRecord
from prediction_feedback.evaluator.target_hit_detector import TargetHitDetector
from prediction_feedback.evaluator.stoploss_detector import StoplossDetector
import logging

logger = logging.getLogger(__name__)

class OutcomeEvaluator:
    """Evaluates a completed prediction against actual market data."""
    
    @staticmethod
    def evaluate(db: Session, record_id: int, exit_price: float, high_price: float, low_price: float, expired: bool = False) -> PredictionRecord:
        """
        Evaluates the prediction and updates the DB.
        In a real app, `high_price` and `low_price` over the holding period would be pulled from D1/D3.
        """
        record = db.query(PredictionRecord).filter(PredictionRecord.id == record_id).first()
        if not record or record.state != "Completed":
            logger.warning(f"Cannot evaluate record {record_id} in state {record.state if record else 'None'}")
            return None
            
        # 1. Detect target and SL hits
        record.hit_target = TargetHitDetector.check_target(record.action, record.target_price, high_price, low_price)
        record.hit_stoploss = StoplossDetector.check_stoploss(record.action, record.stop_loss, high_price, low_price)
        record.expired = expired
        
        # 2. Calculate Actual Return
        if record.entry_price:
            if record.action == "BUY":
                record.actual_return = ((exit_price - record.entry_price) / record.entry_price) * 100
                record.mfe = ((high_price - record.entry_price) / record.entry_price) * 100
                record.mae = ((low_price - record.entry_price) / record.entry_price) * 100
            elif record.action == "SELL":
                record.actual_return = ((record.entry_price - exit_price) / record.entry_price) * 100
                record.mfe = ((record.entry_price - low_price) / record.entry_price) * 100
                record.mae = ((record.entry_price - high_price) / record.entry_price) * 100
                
        # 3. Mark as Evaluated
        record.state = "Evaluated"
        db.commit()
        db.refresh(record)
        
        logger.info(f"Evaluated Prediction {record_id}: Return {record.actual_return:.2f}%, Hit Target: {record.hit_target}, Hit SL: {record.hit_stoploss}")
        return record
