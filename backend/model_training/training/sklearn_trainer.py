import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

class SklearnTrainer:
    def __init__(self, algorithm: str = "LogisticRegression", params: dict = None):
        self.algorithm = algorithm
        self.params = params or {}
        
        if self.algorithm == "LogisticRegression":
            self.model = LogisticRegression(max_iter=1000, random_state=42, **self.params)
        elif self.algorithm == "DecisionTree":
            self.model = DecisionTreeClassifier(random_state=42, **self.params)
        elif self.algorithm == "RandomForest":
            self.model = RandomForestClassifier(random_state=42, **self.params)
        else:
            raise ValueError(f"Unknown sklearn algorithm: {self.algorithm}")
            
        self.feature_names = []
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame = None, y_val: pd.Series = None):
        self.feature_names = X_train.columns.tolist()
        self.model.fit(X_train.fillna(0), y_train)
        
    def predict_proba(self, X: pd.DataFrame):
        return self.model.predict_proba(X.fillna(0))[:, 1]
        
    def get_feature_importance(self):
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return dict(zip(self.feature_names, importances))
        elif hasattr(self.model, "coef_"):
            importances = abs(self.model.coef_[0])
            return dict(zip(self.feature_names, importances))
        return {f: 0.0 for f in self.feature_names}
        
    def save(self, model_id: str, model_dir: str = "models"):
        os.makedirs(model_dir, exist_ok=True)
        path = os.path.join(model_dir, f"{model_id}.joblib")
        joblib.dump(self.model, path)
        
    def load(self, model_id: str, model_dir: str = "models"):
        path = os.path.join(model_dir, f"{model_id}.joblib")
        self.model = joblib.load(path)
