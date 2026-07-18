from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import os
import joblib

class BaseTrainer(ABC):
    """
    Abstract base class for all prediction models in the Model Arena.
    Enforces a common interface for training, prediction, and persistence.
    """
    def __init__(self, params: dict = None, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        self.params = params or {}
        self.model_dir = model_dir
        self.model = None
        self.feature_names = None

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        """
        Trains the model.
        """
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Returns probabilities of the positive class.
        """
        pass
        
    def predict(self, X: pd.DataFrame, threshold=0.5) -> np.ndarray:
        """
        Returns binary predictions based on threshold.
        """
        probas = self.predict_proba(X)
        return (probas >= threshold).astype(int)

    @abstractmethod
    def get_feature_importance(self) -> dict:
        """
        Returns a dictionary mapping feature names to importance scores.
        """
        pass
        
    def save(self, model_id: str):
        """
        Saves the model to disk. Can be overridden for native saving (e.g. lgb.save_model).
        """
        if self.model is None:
            raise ValueError("Model is not trained.")
        os.makedirs(self.model_dir, exist_ok=True)
        path = os.path.join(self.model_dir, f"{model_id}.pkl")
        joblib.dump(self.model, path)
        return path
        
    def load(self, model_id: str):
        """
        Loads the model from disk.
        """
        path = os.path.join(self.model_dir, f"{model_id}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        self.model = joblib.load(path)
