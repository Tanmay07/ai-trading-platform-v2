import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from typing import List

class FeatureSelector:
    def rank_features(self, X: pd.DataFrame, y: pd.Series, top_n: int = 50) -> List[str]:
        if X.empty or len(X) < 10:
            return list(X.columns)
            
        mi = mutual_info_classif(X, y)
        mi_series = pd.Series(mi, index=X.columns)
        mi_series = mi_series.sort_values(ascending=False)
        
        return list(mi_series.head(top_n).index)
