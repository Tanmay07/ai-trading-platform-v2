import pandas as pd
from sklearn.isotonic import IsotonicRegression
from app.config_ml import ml_config

class ProbabilityCalibrator:
    def __init__(self):
        self.method = ml_config.calibration_settings.method
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.is_trained = False
        
    def calibrate(self, uncalibrated_probs: pd.Series, y_true: pd.Series):
        if uncalibrated_probs.empty or y_true.empty:
            return
        self.calibrator.fit(uncalibrated_probs, y_true)
        self.is_trained = True
        
    def predict(self, uncalibrated_probs: pd.Series) -> pd.Series:
        if not self.is_trained or uncalibrated_probs.empty:
            return uncalibrated_probs
            
        calibrated = self.calibrator.predict(uncalibrated_probs)
        return pd.Series(calibrated, index=uncalibrated_probs.index)
