import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from prediction_feedback.storage.database import Base
from prediction_feedback.tracker.prediction_tracker import PredictionTracker
from prediction_feedback.tracker.lifecycle_manager import LifecycleManager
from prediction_feedback.evaluator.outcome_evaluator import OutcomeEvaluator
from prediction_feedback.analytics.confidence_calibrator import ConfidenceCalibrator
from prediction_feedback.explainability.analyzers import SuccessAnalyzer

# Setup in-memory SQLite for testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_prediction_lifecycle(db):
    # 1. Track
    decision = {
        "symbol": "TCS", "action": "BUY", "confidence": 92.5, "final_score": 85.0,
        "regime": "Bull", "explanation": "Test"
    }
    record = PredictionTracker.track_prediction(db, decision)
    assert record.state == "Generated"
    
    # 2. Activate
    active_record = LifecycleManager.activate_prediction(db, record.id, entry_price=100.0, target_price=110.0, stop_loss=95.0)
    assert active_record.state == "Active"
    
    # 3. Complete
    comp_record = LifecycleManager.complete_prediction(db, record.id)
    assert comp_record.state == "Completed"
    
    # 4. Evaluate
    eval_record = OutcomeEvaluator.evaluate(db, record.id, exit_price=112.0, high_price=115.0, low_price=98.0)
    assert eval_record.state == "Evaluated"
    assert eval_record.actual_return == 12.0 # (112-100)/100 = 12%
    assert eval_record.mfe == 15.0
    assert eval_record.mae == -2.0
    assert eval_record.hit_target is True
    assert eval_record.hit_stoploss is False

def test_confidence_calibration(db):
    # Test with the 1 evaluated record we just created (confidence was 92.5)
    # Win rate is 100% since it was a single win
    factor = ConfidenceCalibrator.calculate_calibration_factor(db, 95.0)
    assert factor > 0 # Should calculate successfully

def test_analyzers():
    success = SuccessAnalyzer.analyze("BUY", 15.0, "Bull")
    assert "Strong Trend" in success
    assert "Bull Market Tailwind" in success
