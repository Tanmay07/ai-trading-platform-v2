import xgboost as xgb
import pandas as pd
import numpy as np
import logging
import os
from .base_trainer import BaseTrainer

logger = logging.getLogger("XGBoostTrainer")

class XGBoostTrainer(BaseTrainer):
    def __init__(self, params: dict = None, model_dir: str = None):
        super().__init__(params, model_dir)
        
        self.default_params = {
            'objective': 'binary:logistic',
            'eval_metric': ['auc', 'logloss'],
            'learning_rate': 0.03,
            'max_depth': 6,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'n_estimators': 500,
            'early_stopping_rounds': 50
        }
        self.params = {**self.default_params, **(params or {})}

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        logger.info("Starting XGBoost training...")
        self.feature_names = list(X_train.columns)
        
        n_estimators = self.params.pop('n_estimators', 500)
        early_stopping_rounds = self.params.pop('early_stopping_rounds', 50)
        
        # XGBoost handles early stopping natively in sklearn API but using DMatrix for native
        dtrain = xgb.DMatrix(X_train, label=y_train)
        
        evals = [(dtrain, 'train')]
        if X_val is not None and y_val is not None:
            dval = xgb.DMatrix(X_val, label=y_val)
            evals.append((dval, 'val'))
            
        self.model = xgb.train(
            self.params,
            dtrain,
            num_boost_round=n_estimators,
            evals=evals,
            early_stopping_rounds=early_stopping_rounds if X_val is not None else None,
            verbose_eval=50
        )
        
        logger.info(f"XGBoost training complete. Best iteration: {self.model.best_iteration}")
        return self.model

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        dtest = xgb.DMatrix(X)
        return self.model.predict(dtest, iteration_range=(0, self.model.best_iteration + 1))

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        return self.model.get_score(importance_type='gain')
        
    def save(self, model_id: str):
        if self.model is None:
            raise ValueError("Model is not trained.")
        os.makedirs(self.model_dir, exist_ok=True)
        path = os.path.join(self.model_dir, f"{model_id}.json")
        self.model.save_model(path)
        return path
        
    def load(self, model_id: str):
        path = os.path.join(self.model_dir, f"{model_id}.json")
        self.model = xgb.Booster()
        self.model.load_model(path)
