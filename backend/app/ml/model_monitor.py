import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

class ModelMonitor:
    def calculate_metrics(self, y_true: pd.Series, y_pred_prob: pd.Series, threshold: float = 0.5) -> dict:
        if y_true.empty or y_pred_prob.empty:
            return {}
            
        y_pred = (y_pred_prob >= threshold).astype(int)
        
        try:
            acc = accuracy_score(y_true, y_pred)
            prec = precision_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_true, y_pred_prob)
            
            # Simple Brier score for calibration error
            calib_error = ((y_pred_prob - y_true) ** 2).mean()
            
            return {
                "accuracy": round(float(acc), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1": round(float(f1), 4),
                "roc_auc": round(float(roc_auc), 4),
                "calibration_error": round(float(calib_error), 4)
            }
        except Exception:
            return {}
