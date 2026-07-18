import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, precision_score, recall_score, f1_score, log_loss, brier_score_loss, matthews_corrcoef, cohen_kappa_score
import logging

logger = logging.getLogger("ModelEvaluator")

class ModelEvaluator:
    def __init__(self):
        pass
        
    def evaluate(self, y_true: np.ndarray, y_pred_proba: np.ndarray, threshold: float = 0.5) -> dict:
        """
        Computes both Machine Learning metrics and simulated Investment metrics.
        """
        metrics = {}
        y_pred = (y_pred_proba >= threshold).astype(int)
        
        # 1. Classification Metrics
        try:
            metrics['ROC_AUC'] = roc_auc_score(y_true, y_pred_proba)
            metrics['PR_AUC'] = average_precision_score(y_true, y_pred_proba)
            metrics['Accuracy'] = accuracy_score(y_true, y_pred)
            metrics['Precision'] = precision_score(y_true, y_pred, zero_division=0)
            metrics['Recall'] = recall_score(y_true, y_pred, zero_division=0)
            metrics['F1_Score'] = f1_score(y_true, y_pred, zero_division=0)
            metrics['MCC'] = matthews_corrcoef(y_true, y_pred)
            metrics['Kappa'] = cohen_kappa_score(y_true, y_pred)
            metrics['Log_Loss'] = log_loss(y_true, y_pred_proba)
            metrics['Brier_Score'] = brier_score_loss(y_true, y_pred_proba)
        except Exception as e:
            logger.warning(f"Error computing classification metrics: {e}")
            
        # 2. Simulated Investment Metrics
        # Simplified proxy for investment returns based on predictions
        # Assume a trade wins +2% on True Positive, loses -1% on False Positive
        # False Negatives are missed opportunities (0)
        # True Negatives are avoided losses (0)
        
        trade_returns = []
        for i in range(len(y_true)):
            if y_pred[i] == 1:
                if y_true[i] == 1:
                    trade_returns.append(0.02)
                else:
                    trade_returns.append(-0.01)
                    
        if trade_returns:
            metrics['Win_Rate'] = sum(1 for r in trade_returns if r > 0) / len(trade_returns)
            metrics['Average_Trade_Return'] = np.mean(trade_returns)
            metrics['Total_Return'] = np.sum(trade_returns)
            
            returns_array = np.array(trade_returns)
            gross_profits = returns_array[returns_array > 0].sum()
            gross_losses = np.abs(returns_array[returns_array < 0].sum())
            metrics['Profit_Factor'] = gross_profits / gross_losses if gross_losses > 0 else float('inf')
            
            std_dev = np.std(trade_returns)
            metrics['Sharpe_Ratio'] = np.sqrt(252) * (np.mean(trade_returns) / std_dev) if std_dev > 0 else 0
            
            # Simple Max Drawdown proxy
            cumulative_returns = np.cumsum(trade_returns)
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = peak - cumulative_returns
            metrics['Max_Drawdown'] = np.max(drawdown) if len(drawdown) > 0 else 0
        else:
            metrics['Win_Rate'] = 0.0
            metrics['Average_Trade_Return'] = 0.0
            metrics['Total_Return'] = 0.0
            metrics['Profit_Factor'] = 0.0
            metrics['Sharpe_Ratio'] = 0.0
            metrics['Max_Drawdown'] = 0.0
            
        return metrics
