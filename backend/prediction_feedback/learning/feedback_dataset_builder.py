from sqlalchemy.orm import Session
from prediction_feedback.storage.models import PredictionRecord
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class FeedbackDatasetBuilder:
    """Extracts Evaluated records and exports them as a training dataset."""
    
    @staticmethod
    def build_retraining_dataset(db: Session, export_path: str = "data/feedback_dataset.csv") -> str:
        """
        Dumps evaluated predictions into a CSV/Parquet for D2 ML retraining.
        """
        records = db.query(PredictionRecord).filter(PredictionRecord.state == "Evaluated").all()
        
        if not records:
            logger.info("No evaluated records available to build dataset.")
            return None
            
        data = []
        for r in records:
            # We construct the label: 1 if hit target before stop loss, 0 otherwise
            # For simpler model: 1 if actual_return > 0
            label = 1 if (r.actual_return and r.actual_return > 0) else 0
            
            data.append({
                "symbol": r.symbol,
                "confidence": r.confidence,
                "regime": r.regime,
                "action": r.action,
                "mfe": r.mfe,
                "mae": r.mae,
                "actual_return": r.actual_return,
                "label": label
            })
            
        df = pd.DataFrame(data)
        
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        df.to_csv(export_path, index=False)
        
        logger.info(f"Built retraining dataset with {len(df)} records at {export_path}")
        return export_path
