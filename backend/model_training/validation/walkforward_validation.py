import logging
from model_training.validation.performance_metrics import calculate_ml_metrics, calculate_trading_metrics
from model_training.validation.calibration import ModelCalibrator

logger = logging.getLogger("WalkforwardValidation")

class WalkforwardValidator:
    def __init__(self, trainer):
        self.trainer = trainer
        self.calibrator = ModelCalibrator(method='isotonic')

    def evaluate(self, X_val, y_val, X_test, y_test, returns_test=None):
        """
        Evaluates the trained model on validation and test sets.
        Calibrates the probabilities on the validation set, and tests on the test set.
        """
        logger.info("Starting evaluation and calibration...")
        
        # 1. Raw Predictions on Validation
        val_raw_prob = self.trainer.predict_proba(X_val)
        
        # 2. Fit Calibrator
        self.calibrator.fit(val_raw_prob, y_val)
        
        # 3. Predict on Test
        test_raw_prob = self.trainer.predict_proba(X_test)
        test_cal_prob = self.calibrator.predict_proba(test_raw_prob)
        
        # 4. Metrics
        ml_metrics = calculate_ml_metrics(y_test, test_cal_prob)
        trade_metrics = calculate_trading_metrics(y_test, (test_cal_prob >= 0.5).astype(int), returns_test)
        
        logger.info(f"Test ML Metrics: {ml_metrics}")
        logger.info(f"Test Trade Metrics: {trade_metrics}")
        
        return ml_metrics, trade_metrics, self.calibrator
