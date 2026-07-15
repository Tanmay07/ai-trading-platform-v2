import pandas as pd
from typing import Dict, Any

class ConfusionAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def analyze_label_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyzes the distribution of True labels (future breakouts)"""
        # A true breakout label in our system was defined as 5d > 3% or 7d > 4%
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            # Recreate label
            is_breakout = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            is_breakout = df["is_breakout"]
        else:
            return {"error": "Target columns missing for label distribution"}
            
        total_samples = len(df)
        buy_samples = int(is_breakout.sum())
        hold_samples = total_samples - buy_samples
        
        buy_pct = buy_samples / total_samples if total_samples > 0 else 0
        
        warning = None
        if buy_pct < self.config.get("label_warning_threshold", 0.10):
            warning = f"Warning: Positive rate is extremely low ({buy_pct*100:.2f}%). The model may struggle to learn breakout patterns due to class imbalance."
            
        return {
            "total_samples": total_samples,
            "buy_samples": buy_samples,
            "hold_samples": hold_samples,
            "buy_percentage": round(buy_pct * 100, 2),
            "hold_percentage": round((1 - buy_pct) * 100, 2),
            "warning": warning
        }

    def generate_confusion_matrix(self, df: pd.DataFrame, threshold: float = 50.0) -> Dict[str, Any]:
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        predicted = df["predicted_probability"] >= threshold
        
        tp = int((actual & predicted).sum())
        fp = int((~actual & predicted).sum())
        fn = int((actual & ~predicted).sum())
        tn = int((~actual & ~predicted).sum())
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        accuracy = (tp + tn) / len(df) if len(df) > 0 else 0
        
        return {
            "threshold": threshold,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "accuracy": round(accuracy, 4)
        }
