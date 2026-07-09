import pandas as pd
import logging

logger = logging.getLogger("LeakageDetector")

class LeakageDetector:
    @staticmethod
    def assert_no_leakage(df: pd.DataFrame, feature_cols: list, label_cols: list) -> bool:
        """
        Validates that no feature columns contain forward-looking target data.
        Returns True if safe, False if leakage is detected.
        """
        # Rule 1: No labels allowed in features list
        for label in label_cols:
            if label in feature_cols:
                logger.error(f"LEAKAGE DETECTED: Label column {label} is in the features list.")
                return False
                
        # Rule 2: Explicit exclusion of future-named columns
        future_indicators = ['Target_', 'Next_', 'Future_']
        for feat in feature_cols:
            for ind in future_indicators:
                if feat.startswith(ind):
                    logger.error(f"LEAKAGE DETECTED: Feature {feat} contains a future indicator prefix '{ind}'.")
                    return False
                    
        return True
