import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, log_loss, average_precision_score

def calculate_ml_metrics(y_true, y_prob, threshold=0.5):
    """Calculates standard classification metrics."""
    y_pred = (y_prob >= threshold).astype(int)
    
    # Handle edge case where there's only one class in y_true
    if len(np.unique(y_true)) > 1:
        auc = roc_auc_score(y_true, y_prob)
        logloss = log_loss(y_true, y_prob)
    else:
        auc = 0.5
        logloss = np.nan
        
    return {
        'roc_auc': auc,
        'pr_auc': average_precision_score(y_true, y_prob),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'log_loss': logloss
    }

def calculate_trading_metrics(y_true, y_pred, y_return=None):
    """
    Calculates proxy trading metrics.
    If actual return array is provided, uses it. Otherwise estimates based on Hit Rate.
    """
    win_rate = np.mean(y_true[y_pred == 1]) if sum(y_pred) > 0 else 0
    target_hit_rate = win_rate  # Assuming '1' means hit target >3%
    
    metrics = {
        'win_rate': float(win_rate),
        'target_hit_rate': float(target_hit_rate),
        'total_signals': int(sum(y_pred))
    }
    
    if y_return is not None:
        # Calculate actual returns for the triggered signals
        signal_returns = y_return[y_pred == 1]
        metrics['average_return'] = float(np.mean(signal_returns)) if len(signal_returns) > 0 else 0.0
        
        # Win rate based on positive return vs target
        metrics['positive_return_rate'] = float(np.mean(signal_returns > 0)) if len(signal_returns) > 0 else 0.0
        
    return metrics
