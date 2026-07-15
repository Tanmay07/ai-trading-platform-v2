import pandas as pd
from typing import Dict, Any, List

class RegimeAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
        
    def analyze_regimes(self, df: pd.DataFrame, threshold: float = 65.0) -> List[Dict[str, Any]]:
        """
        Groups predictions into simple Market Regimes (Bull, Bear, Sideways)
        Using a proxy for Regime: If Nifty 50 is not directly available, we will approximate 
        the regime based on average cross-sectional momentum of the day.
        """
        # Ensure we have dates
        if isinstance(df.index, pd.MultiIndex) and "Date" in df.index.names:
            dates = df.index.get_level_values("Date")
        else:
            return [{"error": "Cannot identify Date index for regime mapping."}]
            
        # Determine actual label
        if "Target_Return_5d" in df.columns and "Target_Return_7d" in df.columns:
            actual = (df["Target_Return_5d"] > 0.03) | (df["Target_Return_7d"] > 0.04)
        elif "is_breakout" in df.columns:
            actual = df["is_breakout"]
        else:
            actual = pd.Series([False]*len(df), index=df.index)
            
        predicted = df["predicted_probability"] >= threshold
        
        # Build temp dataframe
        temp = pd.DataFrame({
            "date": dates,
            "actual": actual.values,
            "predicted": predicted.values
        })
        
        # To identify regimes without an external index, we use average win rate or average return of the day 
        # But a more robust way is looking at rolling cross-sectional average of ROC_10 or similar if available
        if "ROC_10" in df.columns:
            # Daily average momentum
            daily_mom = df.groupby(level="Date")["ROC_10"].mean()
            # Assign regime based on 20-day smoothed daily momentum
            smoothed_mom = daily_mom.rolling(window=20, min_periods=1).mean()
            
            def classify_regime(val):
                if val > 2.0: return "Bull"
                if val < -2.0: return "Bear"
                return "Sideways"
                
            regime_map = smoothed_mom.apply(classify_regime)
            temp["regime"] = temp["date"].map(regime_map)
        else:
            # Fallback: time-based split as a mock proxy
            temp["regime"] = "Sideways"
            
        results = []
        for regime, group in temp.groupby("regime"):
            tp = int((group["actual"] & group["predicted"]).sum())
            fp = int((~group["actual"] & group["predicted"]).sum())
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            
            results.append({
                "regime": regime,
                "signals_generated": int(tp + fp),
                "win_rate": round(precision, 4)
            })
            
        return results
