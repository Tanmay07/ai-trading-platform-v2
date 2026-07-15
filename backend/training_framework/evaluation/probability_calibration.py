import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
import logging

logger = logging.getLogger("ProbabilityCalibration")

class CalibratorOptimizer:
    def __init__(self):
        self.platt = LogisticRegression()
        self.isotonic = IsotonicRegression(out_of_bounds='clip')
        self.best_method = None
        self.best_calibrator = None
        
    def fit_and_compare(self, y_prob: np.ndarray, y_true: np.ndarray):
        """
        Fits both calibrators on validation probabilities and targets,
        compares them using Brier Score, and selects the best one.
        """
        logger.info("Comparing Calibration methods...")
        
        if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
            y_prob = y_prob[:, 1]
            
        # Isotonic needs 1D
        self.isotonic.fit(y_prob, y_true)
        iso_preds = self.isotonic.predict(y_prob)
        iso_brier = brier_score_loss(y_true, iso_preds)
        
        # Platt needs 2D (n_samples, 1)
        X_platt = y_prob.reshape(-1, 1)
        self.platt.fit(X_platt, y_true)
        platt_preds = self.platt.predict_proba(X_platt)[:, 1]
        platt_brier = brier_score_loss(y_true, platt_preds)
        
        logger.info(f"Isotonic Brier Score: {iso_brier:.4f}")
        logger.info(f"Platt Scaling Brier Score: {platt_brier:.4f}")
        
        if iso_brier <= platt_brier:
            self.best_method = "isotonic"
            self.best_calibrator = self.isotonic
            logger.info("Selected Isotonic Regression.")
        else:
            self.best_method = "platt"
            self.best_calibrator = self.platt
            logger.info("Selected Platt Scaling (Logistic Regression).")
            
        return {
            "best_method": self.best_method,
            "isotonic_brier": float(iso_brier),
            "platt_brier": float(platt_brier)
        }
        
    def predict_proba(self, y_prob: np.ndarray) -> np.ndarray:
        if self.best_calibrator is None:
            raise ValueError("Calibrator not fitted. Run fit_and_compare first.")
            
        if len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
            y_prob = y_prob[:, 1]
            
        if self.best_method == "platt":
            X_platt = y_prob.reshape(-1, 1)
            return self.best_calibrator.predict_proba(X_platt)[:, 1]
        else:
            return self.best_calibrator.predict(y_prob)
