import random
import time
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger("HyperparameterTuner")

class RandomizedHyperparameterSearch:
    def __init__(self, trainer_class, search_space: Dict[str, List[Any]], cv_engine, n_iter: int = 10, target_metric: str = "roc_auc"):
        """
        Custom Randomized Hyperparameter Search using a specified CV engine (e.g., Purged Walk-Forward).
        
        Args:
            trainer_class: The class (e.g., LightGBMTrainer) to instantiate for training.
            search_space: A dictionary mapping hyperparameter names to lists of possible values.
            cv_engine: An instance of the cross-validator (must implement .split(df)).
            n_iter: Number of random combinations to try.
            target_metric: The metric to optimize (we assume higher is better).
        """
        self.trainer_class = trainer_class
        self.search_space = search_space
        self.cv_engine = cv_engine
        self.n_iter = n_iter
        self.target_metric = target_metric
        self.trials = []
        
    def _sample_params(self) -> Dict[str, Any]:
        params = {}
        for k, v in self.search_space.items():
            params[k] = random.choice(v)
        return params

    def tune(self, df: pd.DataFrame, target_col: str, features: List[str], evaluator) -> Dict[str, Any]:
        """
        Executes the search.
        
        Args:
            df: The full dataset.
            target_col: The column containing the binary labels.
            features: The list of feature columns.
            evaluator: An instance of ModelEvaluator to compute metrics.
            
        Returns:
            The best parameter dictionary found.
        """
        best_score = -np.inf
        best_params = {}
        
        logger.info(f"Starting Randomized Hyperparameter Search for {self.n_iter} iterations.")
        
        for i in range(self.n_iter):
            params = self._sample_params()
            logger.info(f"Trial {i+1}/{self.n_iter} - Params: {params}")
            
            start_time = time.time()
            
            fold_metrics = []
            
            for fold, (train_idx, val_idx) in enumerate(self.cv_engine.split(df)):
                train_df = df.iloc[train_idx]
                val_df = df.iloc[val_idx]
                
                X_train, y_train = train_df[features], train_df[target_col]
                X_val, y_val = val_df[features], val_df[target_col]
                
                # Instantiate trainer with these params
                trainer = self.trainer_class(params=params)
                
                # Train the model (assumes early stopping is handled in trainer if eval sets are provided)
                trainer.train(X_train, y_train, X_val, y_val)
                
                # Evaluate
                y_pred_proba = trainer.predict_proba(X_val)
                metrics = evaluator.evaluate(y_val.values, y_pred_proba)
                fold_metrics.append(metrics)
                
            elapsed = time.time() - start_time
            
            # Average the target metric across folds
            avg_score = np.mean([fm[self.target_metric] for fm in fold_metrics])
            
            trial_result = {
                "iteration": i + 1,
                "params": params,
                "metrics": fold_metrics,
                "avg_score": avg_score,
                "search_time_seconds": elapsed
            }
            self.trials.append(trial_result)
            
            logger.info(f"Trial {i+1} completed in {elapsed:.2f}s - Avg {self.target_metric}: {avg_score:.4f}")
            
            if avg_score > best_score:
                best_score = avg_score
                best_params = params
                logger.info(f"*** New Best Score! {best_score:.4f} ***")
                
        return best_params

    def get_trials(self):
        return self.trials
