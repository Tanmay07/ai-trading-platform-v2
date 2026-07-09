import numpy as pd
import pandas as pd
from app.config_ml import ml_config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DriftDetector:
    def __init__(self):
        self.psi_threshold = ml_config.drift_thresholds.psi_alert_level
        
    def calculate_psi(self, expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) to detect data drift.
        """
        def build_buckets(x, num_buckets):
            try:
                breaks = pd.qcut(x, q=num_buckets, retbins=True, duplicates='drop')[1]
            except ValueError:
                return None
            return breaks
            
        breaks = build_buckets(expected, buckets)
        if breaks is None:
            return 0.0
            
        expected_perc = pd.cut(expected, bins=breaks, include_lowest=True).value_counts(normalize=True)
        actual_perc = pd.cut(actual, bins=breaks, include_lowest=True).value_counts(normalize=True)
        
        # Avoid zero division
        expected_perc = expected_perc.replace(0, 0.0001)
        actual_perc = actual_perc.replace(0, 0.0001)
        
        import numpy as np
        psi = np.sum((actual_perc - expected_perc) * np.log(actual_perc / expected_perc))
        return psi

    def detect_drift(self, df_expected: pd.DataFrame, df_actual: pd.DataFrame) -> dict:
        drift_report = {}
        alert_triggered = False
        
        for col in df_expected.columns:
            if col in df_actual.columns and pd.api.types.is_numeric_dtype(df_expected[col]):
                psi = self.calculate_psi(df_expected[col], df_actual[col])
                drift_report[col] = round(float(psi), 4)
                if psi > self.psi_threshold:
                    alert_triggered = True
                    logger.warning(f"Feature Drift detected in {col}: PSI={psi}")
                    
        return {
            "drift_detected": alert_triggered,
            "psi_scores": drift_report
        }
