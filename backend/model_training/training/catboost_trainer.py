import catboost as cb
import pandas as pd
import numpy as np
import logging
import os
from .base_trainer import BaseTrainer

logger = logging.getLogger("CatBoostTrainer")

class CatBoostTrainer(BaseTrainer):
    def __init__(self, params: dict = None, model_dir: str = None):
        super().__init__(params, model_dir)
        
        self.default_params = {
            'loss_function': 'Logloss',
            'eval_metric': 'AUC',
            'learning_rate': 0.03,
            'depth': 6,
            'iterations': 500,
            'od_type': 'Iter',
            'od_wait': 50,
            'verbose': 50
        }
        self.params = {**self.default_params, **(params or {})}
        self.model = cb.CatBoostClassifier(**self.params)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        logger.info("Starting CatBoost training...")
        self.feature_names = list(X_train.columns)
        
        eval_set = None
        if X_val is not None and y_val is not None:
            eval_set = (X_val, y_val)
            
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            early_stopping_rounds=self.params.get('od_wait', 50),
            use_best_model=True if eval_set else False
        )
        
        logger.info(f"CatBoost training complete. Best iteration: {self.model.get_best_iteration()}")
        return self.model

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.model.is_fitted():
            raise ValueError("Model has not been trained yet.")
        # CatBoost returns [prob_0, prob_1], we want prob_1
        return self.model.predict_proba(X)[:, 1]

    def get_feature_importance(self) -> dict:
        if not self.model.is_fitted():
            return {}
        importance = self.model.get_feature_importance()
        return dict(zip(self.feature_names, importance))
        
    def save(self, model_id: str):
        if not self.model.is_fitted():
            raise ValueError("Model is not trained.")
        os.makedirs(self.model_dir, exist_ok=True)
        path = os.path.join(self.model_dir, f"{model_id}.cbm")
        self.model.save_model(path)
        return path
        
    def load(self, model_id: str):
        path = os.path.join(self.model_dir, f"{model_id}.cbm")
        self.model = cb.CatBoostClassifier()
        self.model.load_model(path)
