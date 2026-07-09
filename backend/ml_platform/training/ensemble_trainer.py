import logging
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.ensemble import VotingClassifier
import pandas as pd

logger = logging.getLogger(__name__)

class EnsembleTrainer:
    """Trains LightGBM, XGBoost, and CatBoost models and creates a voting ensemble."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        
        # Initialize base models
        self.lgbm = LGBMClassifier(random_state=random_state, n_estimators=100, learning_rate=0.05, verbose=-1)
        self.xgb = XGBClassifier(random_state=random_state, n_estimators=100, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss')
        self.cat = CatBoostClassifier(random_state=random_state, iterations=100, learning_rate=0.05, verbose=0)
        
        # The ensemble
        self.ensemble = VotingClassifier(
            estimators=[
                ('lgbm', self.lgbm),
                ('xgb', self.xgb),
                ('cat', self.cat)
            ],
            voting='soft'
        )

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Trains the ensemble on the provided dataset."""
        logger.info("Training LightGBM, XGBoost, and CatBoost ensemble...")
        
        # Handle Categorical features implicitly if any (CatBoost needs explicit strings usually, 
        # but we use all numerical in feature_engineering)
        
        self.ensemble.fit(X_train, y_train)
        logger.info("Ensemble training complete.")
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.ensemble.predict(X)
        
    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.ensemble.predict_proba(X)
