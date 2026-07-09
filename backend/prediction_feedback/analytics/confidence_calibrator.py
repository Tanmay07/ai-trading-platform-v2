from sqlalchemy.orm import Session
from sqlalchemy import func
from prediction_feedback.storage.models import PredictionRecord
import logging

logger = logging.getLogger(__name__)

class ConfidenceCalibrator:
    """Recalibrates confidence scores based on historical accuracy of past predictions."""
    
    @staticmethod
    def calculate_calibration_factor(db: Session, target_confidence_bucket: float) -> float:
        """
        Calculates the actual win rate for a given confidence bucket (e.g. 90-100%).
        Returns a modifier (e.g. 0.95 means predictions were 5% less accurate than expected).
        """
        lower_bound = target_confidence_bucket - 5.0
        upper_bound = target_confidence_bucket + 5.0
        
        records = db.query(PredictionRecord).filter(
            PredictionRecord.state == "Evaluated",
            PredictionRecord.confidence >= lower_bound,
            PredictionRecord.confidence <= upper_bound
        ).all()
        
        if not records:
            return 1.0 # No data, assume perfectly calibrated
            
        wins = sum(1 for r in records if r.actual_return and r.actual_return > 0)
        actual_win_rate = (wins / len(records)) * 100
        
        # E.g. expected 95%, actual 80% -> factor = 80/95 = 0.84
        factor = actual_win_rate / target_confidence_bucket
        
        # Don't let it swing too wildly
        return max(0.5, min(1.5, factor))
