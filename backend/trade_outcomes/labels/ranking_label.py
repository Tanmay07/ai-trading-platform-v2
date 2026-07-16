import pandas as pd
import logging

logger = logging.getLogger("RankingLabeler")

class RankingLabeler:
    """
    Generates labels by ranking symbols cross-sectionally for every trading day.
    Top X% of performers get a Positive label (1), the rest Negative (0).
    """
    
    def __init__(self, top_percentile: float = 5.0, metric_col: str = 'Trade_Quality_Score'):
        self.top_percentile = top_percentile / 100.0
        self.metric_col = metric_col
        
    def generate_labels(self, df: pd.DataFrame) -> pd.Series:
        if self.metric_col not in df.columns:
            raise ValueError(f"Metric column {self.metric_col} is missing from DataFrame.")
            
        # Ensure we have Date in index
        if 'Date' not in df.index.names:
            logger.error("Date must be in the index to perform cross-sectional daily ranking.")
            return pd.Series(0, index=df.index)
            
        # Group by Date and rank
        def rank_daily(group):
            # Quantile threshold (e.g. 0.95 for top 5%)
            threshold = group.quantile(1.0 - self.top_percentile)
            return (group >= threshold).astype(int)
            
        # We need to unstack or group. Since Date is in index, we can just group by level='Date'
        # But wait, we only want to rank the metric column
        ranks = df[self.metric_col].groupby(level='Date').transform(rank_daily)
        
        # Ensure the index aligns back properly by sorting index to match original if needed,
        # but apply usually preserves the original index shape if no aggregation.
        # Since df index is Date with duplicates, we just return ranks directly.
        return ranks.values
