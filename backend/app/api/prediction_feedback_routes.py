from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from prediction_feedback.storage.database import get_feedback_db
from prediction_feedback.storage.models import PredictionRecord
from prediction_feedback.tracker.lifecycle_manager import LifecycleManager
from prediction_feedback.evaluator.outcome_evaluator import OutcomeEvaluator
from prediction_feedback.explainability.analyzers import SuccessAnalyzer, FailureAnalyzer
from prediction_feedback.learning.feedback_dataset_builder import FeedbackDatasetBuilder

import random

router = APIRouter(prefix="/api/predictions", tags=["Prediction Feedback Engine"])

@router.get("/")
def get_predictions(db: Session = Depends(get_feedback_db)):
    """Fetches all tracked predictions."""
    records = db.query(PredictionRecord).all()
    return {"predictions": records}

@router.post("/evaluate")
def evaluate_completed_predictions(background_tasks: BackgroundTasks, db: Session = Depends(get_feedback_db)):
    """
    Manually triggers the evaluation of all 'Completed' predictions.
    Normally this would run on a cron schedule at EOD.
    """
    completed = db.query(PredictionRecord).filter(PredictionRecord.state == "Completed").all()
    
    evaluated_count = 0
    for record in completed:
        # MOCK DATA: In a real app, fetch actual high/low prices from D1/D3 Market Data
        # For this test, let's randomly simulate success or failure
        if random.choice([True, False]):
            # Success mock
            exit_price = record.entry_price * 1.06
            high_price = record.entry_price * 1.08
            low_price = record.entry_price * 0.98
        else:
            # Failure mock
            exit_price = record.entry_price * 0.96
            high_price = record.entry_price * 1.02
            low_price = record.entry_price * 0.94
            
        evaluated_record = OutcomeEvaluator.evaluate(
            db=db,
            record_id=record.id,
            exit_price=exit_price,
            high_price=high_price,
            low_price=low_price
        )
        
        # Analyze reasoning
        if evaluated_record.actual_return and evaluated_record.actual_return > 0:
            evaluated_record.success_factors = SuccessAnalyzer.analyze(evaluated_record.action, evaluated_record.mfe, evaluated_record.regime)
        else:
            evaluated_record.failure_factors = FailureAnalyzer.analyze(evaluated_record.action, evaluated_record.mae, evaluated_record.regime)
            
        db.commit()
        evaluated_count += 1
        
    return {"status": "Evaluated", "count": evaluated_count}

@router.post("/build_dataset")
def build_retraining_dataset(db: Session = Depends(get_feedback_db)):
    """Dumps evaluated predictions into a CSV for ML retraining."""
    path = FeedbackDatasetBuilder.build_retraining_dataset(db)
    if path:
        return {"status": "Success", "dataset_path": path}
    return {"status": "No data available"}
