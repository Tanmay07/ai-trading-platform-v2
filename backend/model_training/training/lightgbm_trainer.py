import lightgbm as lgb
import pandas as pd
import numpy as np
import logging
import os
from .base_trainer import BaseTrainer

logger = logging.getLogger("LightGBMTrainer")

class LightGBMTrainer(BaseTrainer):
    def __init__(self, params: dict = None, model_dir: str = None):
        super().__init__(params, model_dir)
        self.default_params = {
            'objective': 'binary',
            'metric': ['auc', 'binary_logloss'],
            'learning_rate': 0.03,
            'num_leaves': 64,
            'max_depth': 8,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'n_estimators': 500,
            'verbose': -1,
            'early_stopping_rounds': 50
        }
        
        self.params = {**self.default_params, **(params or {})}

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        logger.info("Starting LightGBM training...")
        self.feature_names = list(X_train.columns)
        
        train_data = lgb.Dataset(X_train, label=y_train)
        
        valid_sets = [train_data]
        valid_names = ['train']
        
        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            valid_names.append('val')
        
        num_boost_round = self.params.pop('n_estimators', 500)
        early_stopping = self.params.pop('early_stopping_rounds', 50)
        
        callbacks = [lgb.log_evaluation(period=50)]
        if X_val is not None:
            callbacks.append(lgb.early_stopping(stopping_rounds=early_stopping, verbose=True))
        
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=num_boost_round,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=callbacks
        )
        
        logger.info(f"Training complete. Best iteration: {self.model.best_iteration}")
        return self.model

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X, num_iteration=self.model.best_iteration)
        
    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importance(importance_type='gain')
        return dict(zip(self.feature_names, importance))
        
    def save(self, model_id: str):
        if self.model is None:
            raise ValueError("Model is not trained.")
        os.makedirs(self.model_dir, exist_ok=True)
        path = os.path.join(self.model_dir, f"{model_id}.txt")
        self.model.save_model(path)
        return path
        
    def load(self, model_id: str):
        path = os.path.join(self.model_dir, f"{model_id}.txt")
        self.model = lgb.Booster(model_file=path)
