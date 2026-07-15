import numpy as np
from sklearn.isotonic import IsotonicRegression
import logging

logger = logging.getLogger("Calibrator")

class ModelCalibrator:
    def __init__(self, method='isotonic'):
        self.method = method
        self.calibrator = None

    def fit(self, y_prob, y_true):
        """Fits the calibrator using validation probabilities."""
        logger.info(f"Fitting {self.method} calibrator...")
        if self.method == 'isotonic':
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(y_prob, y_true)
        else:
            raise NotImplementedError("Only isotonic regression is currently supported.")
            
    def predict_proba(self, y_prob):
        """Transforms raw probabilities to calibrated probabilities."""
        if self.calibrator is None:
            logger.warning("Calibrator not fitted. Returning raw probabilities.")
            return y_prob
            
        if self.method == 'isotonic':
            return self.calibrator.predict(y_prob)
