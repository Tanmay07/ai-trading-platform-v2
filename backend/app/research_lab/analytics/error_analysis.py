import pandas as pd
from typing import Dict, Any, List

class ErrorAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def analyze_errors(self, df: pd.DataFrame, threshold: float = 65.0) -> Dict[str, Any]:
        """
        Extracts False Positives and False Negatives, along with their key attributes.
        """
        # Determine actual label
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        predicted = df["predicted_probability"] >= threshold
        
        # Determine symbol and date
        symbols = None
        dates = None
        if "symbol" in df.columns:
            symbols = df["symbol"]
        elif isinstance(df.index, pd.MultiIndex) and "Symbol" in df.index.names:
            symbols = df.index.get_level_values("Symbol")
            
        if isinstance(df.index, pd.MultiIndex) and "Date" in df.index.names:
            dates = df.index.get_level_values("Date")
        else:
            dates = df.index # fallback
            
        temp = pd.DataFrame({
            "symbol": symbols if symbols is not None else "Unknown",
            "date": dates,
            "actual": actual.values,
            "prob": df["predicted_probability"].values
        })
        
        fp_mask = (~actual & predicted)
        fn_mask = (actual & ~predicted)
        
        fp_df = temp[fp_mask].sort_values("prob", ascending=False)
        fn_df = temp[fn_mask].sort_values("prob", ascending=True)
        
        top_k = self.config.get("top_errors_to_analyze", 100)
        
        false_positives = []
        for _, row in fp_df.head(top_k).iterrows():
            false_positives.append({
                "symbol": str(row["symbol"]),
                "date": str(row["date"])[:10],
                "predicted_prob": round(row["prob"], 2)
            })
            
        false_negatives = []
        for _, row in fn_df.head(top_k).iterrows():
            false_negatives.append({
                "symbol": str(row["symbol"]),
                "date": str(row["date"])[:10],
                "predicted_prob": round(row["prob"], 2)
            })
            
        return {
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }
