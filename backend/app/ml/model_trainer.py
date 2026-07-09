import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from app.config_ml import ml_config
import pandas as pd

class ModelTrainer:
    def __init__(self):
        self.params = ml_config.model_parameters

    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series):
        model = xgb.XGBClassifier(**self.params.xgboost.model_dump(), use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)
        return model

    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series):
        model = lgb.LGBMClassifier(**self.params.lightgbm.model_dump())
        model.fit(X_train, y_train)
        return model

    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series):
        model = RandomForestClassifier(**self.params.random_forest.model_dump())
        model.fit(X_train, y_train)
        return model
