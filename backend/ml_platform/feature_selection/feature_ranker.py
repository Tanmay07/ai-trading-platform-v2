import logging
import pandas as pd

logger = logging.getLogger(__name__)

class FeatureRanker:
    """
    Ranks features using various methods.
    Since SHAP requires specific python versions, this serves as a graceful fallback wrapper.
    """
    
    @staticmethod
    def rank_features_tree_importance(model, feature_names: list) -> pd.DataFrame:
        """
        Uses standard feature importances available in XGBoost/LightGBM/CatBoost.
        """
        try:
            importances = model.feature_importances_
            
            df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            })
            return df.sort_values(by='Importance', ascending=False)
            
        except AttributeError:
            logger.warning("Model does not support standard feature_importances_")
            return pd.DataFrame()
            
    @staticmethod
    def try_shap_importance(model, X_val: pd.DataFrame) -> pd.DataFrame:
        """
        Attempts to calculate SHAP values if the library is installed.
        Gracefully handles ImportError.
        """
        try:
            import shap
            logger.info("Calculating SHAP values...")
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_val)
            
            # For classification, shap_values might be a list
            if isinstance(shap_values, list):
                shap_values = shap_values[1] # Use class 1 (positive)
                
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
            return pd.DataFrame({
                'Feature': X_val.columns,
                'SHAP_Importance': mean_abs_shap
            }).sort_values(by='SHAP_Importance', ascending=False)
            
        except ImportError:
            logger.warning("SHAP is not installed. Skipping SHAP importance.")
            return pd.DataFrame()
