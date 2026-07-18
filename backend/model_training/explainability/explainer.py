import shap
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("ModelExplainer")

class ModelExplainer:
    def __init__(self, model):
        """
        Initializes the explainer. Model should be the native booster object.
        """
        self.model = model
        
    def generate_global_importance(self, feature_names: list, X_sample: pd.DataFrame) -> dict:
        """
        Generates TreeSHAP based global feature importance.
        """
        try:
            # Create TreeExplainer
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_sample)
            
            # For some models/objectives, shap_values is a list of arrays (one per class)
            if isinstance(shap_values, list):
                shap_values = shap_values[1] # positive class
                
            # Calculate mean absolute SHAP value for each feature
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
            importance_dict = {
                name: float(val) 
                for name, val in zip(feature_names, mean_abs_shap)
            }
            
            # Sort by importance descending
            return dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
            
        except Exception as e:
            logger.warning(f"Failed to generate SHAP explanations: {e}")
            return {}
