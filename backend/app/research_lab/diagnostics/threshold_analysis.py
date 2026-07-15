import pandas as pd
from typing import Dict, Any, List

class ThresholdAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def analyze_thresholds(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        results = []
        
        # Determine actual label (Future Return >= 5% in 7 days or similar for demonstration)
        # Using the standard label
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        thresholds = self.config.get("thresholds_to_test", [55, 60, 65, 70, 75, 80])
        
        for t in thresholds:
            predicted = df["predicted_probability"] >= t
            
            tp = int((actual & predicted).sum())
            fp = int((~actual & predicted).sum())
            fn = int((actual & ~predicted).sum())
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            # Win rate (assuming trades only taken on predicted positive)
            win_rate = tp / (tp + fp) if (tp + fp) > 0 else 0
            
            results.append({
                "threshold": t,
                "positive_samples": int(predicted.sum()),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "expected_trades": int(predicted.sum()),
                "win_rate": round(win_rate, 4)
            })
            
        return results
        
    def recommend_optimal_threshold(self, thresholds_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommends optimal threshold balancing Win Rate (> 50%) and Expected Trades.
        """
        valid = [t for t in thresholds_data if t["win_rate"] >= 0.50 and t["expected_trades"] > 0]
        
        if not valid:
            # If none are above 50%, pick the highest win rate
            best = max(thresholds_data, key=lambda x: x["win_rate"])
            reason = "No threshold achieves >50% win rate. Selected highest relative win rate."
        else:
            # Pick the one with the highest expected trades that still meets win rate
            best = max(valid, key=lambda x: x["expected_trades"])
            reason = "Optimal balance of Win Rate (>50%) and highest trade frequency."
            
        return {
            "optimal_threshold": best["threshold"],
            "expected_win_rate": best["win_rate"],
            "expected_trades": best["expected_trades"],
            "reason": reason
        }
