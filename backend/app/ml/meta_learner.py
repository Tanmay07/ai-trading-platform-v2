import pandas as pd
from sklearn.linear_model import LogisticRegression

class MetaLearner:
    def __init__(self):
        self.model = LogisticRegression(class_weight='balanced')
        self.is_trained = False
        
    def train(self, X_meta: pd.DataFrame, y: pd.Series):
        """
        X_meta should contain ensemble predictions, AI consensus score, and market score.
        """
        if X_meta.empty or y.empty:
            return
        self.model.fit(X_meta, y)
        self.is_trained = True
        
    def predict_proba(self, X_meta: pd.DataFrame) -> pd.Series:
        if not self.is_trained or X_meta.empty:
            return pd.Series(0.5, index=X_meta.index) # Fallback
            
        probs = self.model.predict_proba(X_meta)[:, 1]
        return pd.Series(probs, index=X_meta.index)
