import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score, precision_score, 
    recall_score, f1_score, log_loss, brier_score_loss, matthews_corrcoef, 
    cohen_kappa_score, balanced_accuracy_score
)
from sklearn.calibration import calibration_curve
import logging

logger = logging.getLogger("ModelEvaluator")

class ModelEvaluator:
    def __init__(self):
        pass
        
    def evaluate(self, y_true: np.ndarray, y_pred_proba: np.ndarray, threshold: float = 0.5) -> dict:
        """
        Computes Machine Learning and Calibration metrics.
        """
        metrics = {}
        y_pred = (y_pred_proba >= threshold).astype(int)
        
        # 1. Classification Metrics
        try:
            metrics['ROC_AUC'] = float(roc_auc_score(y_true, y_pred_proba))
            metrics['PR_AUC'] = float(average_precision_score(y_true, y_pred_proba))
            metrics['Accuracy'] = float(accuracy_score(y_true, y_pred))
            metrics['Balanced_Accuracy'] = float(balanced_accuracy_score(y_true, y_pred))
            metrics['Precision'] = float(precision_score(y_true, y_pred, zero_division=0))
            metrics['Recall'] = float(recall_score(y_true, y_pred, zero_division=0))
            metrics['F1_Score'] = float(f1_score(y_true, y_pred, zero_division=0))
            metrics['MCC'] = float(matthews_corrcoef(y_true, y_pred))
            metrics['Kappa'] = float(cohen_kappa_score(y_true, y_pred))
            metrics['Log_Loss'] = float(log_loss(y_true, y_pred_proba))
            metrics['Brier_Score'] = float(brier_score_loss(y_true, y_pred_proba))
        except Exception as e:
            logger.warning(f"Error computing classification metrics: {e}")
            
        # 2. Calibration Analysis
        try:
            prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=10)
            metrics['Calibration_Reliability'] = float(np.mean(np.abs(prob_true - prob_pred)))
            # If Reliability is close to 0, model is well calibrated. 
        except Exception as e:
            logger.warning(f"Error computing calibration metrics: {e}")
            metrics['Calibration_Reliability'] = 1.0 # Worst case
            
        return metrics
