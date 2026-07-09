import logging
import pandas as pd
from typing import Dict, Any

from ml_platform.training.ensemble_trainer import EnsembleTrainer
from ml_platform.datasets.data_splitter import DataSplitter
from ml_platform.validation.model_validator import ModelValidator

logger = logging.getLogger(__name__)

class WalkforwardTrainer:
    """Orchestrates time-series walk-forward cross validation."""
    
    @staticmethod
    def run_walkforward_cv(X: pd.DataFrame, y: pd.Series, train_months: int = 24, test_months: int = 6) -> Dict[str, Any]:
        logger.info(f"Starting walk-forward CV (Train: {train_months}m, Test: {test_months}m)")
        
        # Combine X and y temporarily for splitting
        df_full = pd.concat([X, y], axis=1)
        target_col = y.name
        
        splitter = DataSplitter()
        splits = splitter.walk_forward_split(df_full, train_months, test_months)
        
        fold = 1
        all_metrics = []
        best_model = None
        best_f1 = 0
        
        for train_df, test_df in splits:
            if len(train_df) < 100 or len(test_df) < 10:
                continue
                
            logger.info(f"Fold {fold}: Train size {len(train_df)}, Test size {len(test_df)}")
            
            X_train = train_df.drop(columns=[target_col])
            y_train = train_df[target_col]
            
            X_test = test_df.drop(columns=[target_col])
            y_test = test_df[target_col]
            
            trainer = EnsembleTrainer()
            trainer.train(X_train, y_train)
            
            # Predict and validate
            y_pred = trainer.predict(X_test)
            y_prob = trainer.predict_proba(X_test)
            
            # Usually predict_proba returns a 2D array. We pass the prob of the positive class if binary.
            prob_1d = None
            if y_prob.shape[1] == 2:
                prob_1d = y_prob[:, 1]
            elif y_prob.shape[1] > 2:
                # Multiclass, handle differently or omit ROC/Brier for now
                pass 
                
            # The ModelValidator takes y_prob_1d, we'll patch that dynamically
            metrics = ModelValidator.validate_classification(y_test, y_pred, y_prob=None)
            
            # Simple hack for roc_auc if binary:
            if prob_1d is not None and len(y_test.unique()) == 2:
                from sklearn.metrics import roc_auc_score, brier_score_loss
                try:
                    metrics['roc_auc'] = roc_auc_score(y_test, prob_1d)
                    metrics['brier_score'] = brier_score_loss(y_test, prob_1d)
                except:
                    pass
            
            all_metrics.append(metrics)
            
            # Track best model based on F1
            if metrics.get('f1', 0) > best_f1:
                best_f1 = metrics.get('f1', 0)
                best_model = trainer.ensemble
                
            fold += 1
            
        # Aggregate metrics
        avg_metrics = {}
        if all_metrics:
            keys = all_metrics[0].keys()
            for key in keys:
                avg_metrics[key] = sum(m.get(key, 0) for m in all_metrics) / len(all_metrics)
                
        logger.info(f"Walk-forward CV Complete. Avg Metrics: {avg_metrics}")
        
        return {
            "avg_metrics": avg_metrics,
            "best_model": best_model,
            "folds_completed": fold - 1
        }
