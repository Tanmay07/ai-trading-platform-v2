import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("SHAPAnalysis")

class SHAPAnalyzer:
    def __init__(self, model):
        self.model = model
        
    def generate_shap_values(self, X: pd.DataFrame):
        """
        Uses LightGBM's native pred_contrib=True to generate SHAP values.
        This completely bypasses the need for the `shap` Python package,
        making it perfectly compatible with Python 3.14.
        """
        logger.info("Generating native SHAP values...")
        # pred_contrib returns matrix of shape (n_samples, n_features + 1)
        # The last column is the expected value (base value).
        shap_matrix = self.model.predict(X, num_iteration=self.model.best_iteration, pred_contrib=True)
        
        shap_values = shap_matrix[:, :-1]
        base_value = shap_matrix[0, -1]
        
        return shap_values, base_value
        
    def get_summary_stats(self, shap_values: np.ndarray, feature_names: list, top_n: int = 20):
        """
        Calculates mean absolute SHAP values for global summary.
        """
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        df = pd.DataFrame({
            'feature': feature_names,
            'mean_abs_shap': mean_abs_shap
        })
        
        return df.sort_values(by='mean_abs_shap', ascending=False).head(top_n).reset_index(drop=True)
