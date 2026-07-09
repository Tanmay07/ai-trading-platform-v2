import pandas as pd
import yaml

class EventSplitter:
    """
    Filters a dataset to only include rows near specific dates.
    """
    def __init__(self):
        with open("config/scenario_dataset.yaml", "r") as f:
            self.config = yaml.safe_load(f)["scenario_datasets"]["events"]
            
    def split(self, df: pd.DataFrame, event_name: str) -> pd.DataFrame:
        if df.empty or event_name not in self.config:
            return pd.DataFrame()
            
        event_cfg = self.config[event_name]
        window = event_cfg["window_days"]
        dates = pd.to_datetime(event_cfg["dates"])
        
        # We want to keep any row whose Date index is within window days of any event date
        mask = pd.Series(False, index=df.index)
        
        for d in dates:
            start_d = d - pd.Timedelta(days=window)
            end_d = d + pd.Timedelta(days=window)
            mask = mask | ((df.index >= start_d) & (df.index <= end_d))
            
        return df[mask]
