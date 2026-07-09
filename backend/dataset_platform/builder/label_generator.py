import pandas as pd
from dataset_platform.labeling.breakout_labels import BreakoutLabels
from dataset_platform.labeling.classification_labels import ClassificationLabels

class LabelGenerator:
    """
    Master orchestrator for generating all configured labels.
    """
    @staticmethod
    def generate_all(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
            
        # Add Breakout
        df = BreakoutLabels().generate(df)
        
        # Add Classification
        df = ClassificationLabels().generate(df)
        
        # In a real environment, we drop rows where Target is NaN (end of time series)
        # But we do that in the DatasetBuilder after joining so we don't lose data prematurely
        return df
