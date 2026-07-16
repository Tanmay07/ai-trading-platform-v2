import logging
import pandas as pd
from typing import List, Dict, Any
from benchmarking.datasets.dataset_selector import DatasetSelector

logger = logging.getLogger("RedundancyDetector")

class RedundancyDetector:
    def __init__(self):
        self.selector = DatasetSelector()
        
    def detect_redundancies(self, threshold: float = 0.95) -> List[Dict[str, Any]]:
        """
        Calculates correlation matrix on the Hybrid dataset.
        Flags any raw feature that is highly correlated with an Institutional Factor.
        """
        logger.info(f"Detecting redundancies (corr > {threshold})...")
        df = self.selector.load_mode("hybrid")
        
        # Only numeric cols
        num_cols = df.select_dtypes(include=['number']).columns
        # Drop identifiers
        num_cols = [c for c in num_cols if c not in ['symbol', 'Target_Breakout_Success', 'Target_Return_5d']]
        
        # We don't want to calculate a massive 1000x1000 matrix if possible, 
        # but pandas corr() is fast enough for <100 columns.
        corr_matrix = df[num_cols].corr().abs()
        
        factors = [f for f in self.selector.factors if f in corr_matrix.columns]
        raw_features = [c for c in corr_matrix.columns if c not in factors]
        
        redundancies = []
        
        for raw in raw_features:
            for factor in factors:
                corr_val = corr_matrix.loc[raw, factor]
                if corr_val > threshold:
                    redundancies.append({
                        "raw_feature": raw,
                        "covered_by_factor": factor,
                        "correlation": float(corr_val),
                        "recommendation": f"Deprecate '{raw}' (Highly captured by '{factor}')"
                    })
                    
        return sorted(redundancies, key=lambda x: x["correlation"], reverse=True)
