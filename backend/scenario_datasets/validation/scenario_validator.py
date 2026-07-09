import pandas as pd
import yaml
import logging

logger = logging.getLogger("ScenarioValidator")

class ScenarioValidator:
    """
    Ensures a segmented scenario dataset has enough data to be statistically significant.
    """
    def __init__(self):
        with open("config/scenario_dataset.yaml", "r") as f:
            self.config = yaml.safe_load(f)["scenario_datasets"]["validation"]
            
    def validate(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {"valid": False, "score": 0.0, "reason": "Empty dataset"}
            
        rows = len(df)
        symbols = df['Symbol'].nunique() if 'Symbol' in df.columns else 0
        
        score = 100.0
        reasons = []
        
        if rows < self.config["min_rows"]:
            score -= 50
            reasons.append(f"Insufficient rows: {rows} < {self.config['min_rows']}")
            
        if symbols < self.config["min_symbols"]:
            score -= 50
            reasons.append(f"Insufficient symbol diversity: {symbols} < {self.config['min_symbols']}")
            
        return {
            "valid": score >= 100.0,
            "score": score,
            "reason": "; ".join(reasons) if reasons else "Valid"
        }
