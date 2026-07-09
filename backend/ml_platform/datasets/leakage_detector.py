import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LeakageDetector:
    """Detects data leakage in ML datasets."""
    
    @staticmethod
    def assert_no_leakage(df: pd.DataFrame, feature_cols: list, label_cols: list) -> bool:
        """
        Ensures that features do not accidentally contain target information.
        Basic check: are label columns inside the feature columns?
        """
        leaks = [col for col in label_cols if col in feature_cols]
        if leaks:
            logger.error(f"DATA LEAKAGE DETECTED! Features contain targets: {leaks}")
            return False
            
        # Additional checks could be added here (e.g. checking correlation of features with targets)
        return True
