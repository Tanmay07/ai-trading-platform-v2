import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)

class ModelValidator:
    """Calculates classification and regression metrics for model validation."""
    
    @staticmethod
    def validate_classification(y_true, y_pred, y_prob=None) -> dict:
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
            "f1": f1_score(y_true, y_pred, average='weighted', zero_division=0)
        }
        
        if y_prob_1d is not None and len(np.unique(y_true)) == 2:
            try:
                metrics["roc_auc"] = roc_auc_score(y_true, y_prob_1d)
                metrics["brier_score"] = brier_score_loss(y_true, y_prob_1d)
            except Exception as e:
                logger.warning(f"Could not calculate ROC/Brier: {e}")
                
        return metrics

    @staticmethod
    def validate_regression(y_true, y_pred) -> dict:
        return {
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2": r2_score(y_true, y_pred)
        }
