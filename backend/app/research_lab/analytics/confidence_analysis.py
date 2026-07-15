import pandas as pd
from typing import Dict, Any, List

class ConfidenceAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def analyze_calibration(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Buckets predictions into confidence brackets and measures actual win rate per bracket.
        """
        # Determine actual label
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        temp = pd.DataFrame({
            "actual": actual.values,
            "prob": df["predicted_probability"].values
        })
        
        bins = [0, 50, 60, 70, 80, 90, 100]
        labels = ["<50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
        
        temp["bucket"] = pd.cut(temp["prob"], bins=bins, labels=labels, right=False)
        
        results = []
        warning = None
        for label in labels:
            group = temp[temp["bucket"] == label]
            samples = len(group)
            if samples > 0:
                win_rate = group["actual"].mean()
                results.append({
                    "bucket": label,
                    "samples": samples,
                    "actual_win_rate": round(float(win_rate), 4)
                })
                
                # Calibration warning check
                if label == "90-100%" and win_rate < (0.90 - self.config.get("calibration_warning_threshold", 0.15)):
                    warning = f"Calibration Warning: Predictions in 90-100% bucket only achieved {win_rate*100:.1f}% accuracy."
                    
        return {
            "buckets": results,
            "warning": warning
        }
