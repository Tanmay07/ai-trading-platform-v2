import pandas as pd
import numpy as np

class InstitutionalFactor:
    """
    Base class for all Institutional Factors.
    Supports fixed "Research" weights and "Adaptive" weights.
    Always outputs a score bounded between 0 and 100.
    """
    def __init__(self, name: str, config: dict, adaptive_mode: bool = False):
        self.name = name
        self.weights = config.get(name, {})
        self.adaptive_mode = adaptive_mode
        self.adaptive_weights = {} # Placeholder for Phase F

    def _normalize_0_100(self, series: pd.Series) -> pd.Series:
        """Min-Max scaler bound to 0-100, robust to outliers (clips at 1st/99th percentile)"""
        if len(series.dropna()) == 0:
            return pd.Series(50.0, index=series.index)
            
        p1 = series.quantile(0.01)
        p99 = series.quantile(0.99)
        
        # Avoid division by zero
        if p99 == p1:
            return pd.Series(50.0, index=series.index)
            
        clipped = series.clip(lower=p1, upper=p99)
        normalized = ((clipped - p1) / (p99 - p1)) * 100.0
        return normalized.fillna(50.0)

    def get_weights(self) -> dict:
        if self.adaptive_mode and self.adaptive_weights:
            return self.adaptive_weights
        return self.weights
        
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        """
        Must be implemented by subclasses.
        Returns a Pandas Series with the 0-100 factor score.
        """
        raise NotImplementedError("Subclasses must implement calculate()")
