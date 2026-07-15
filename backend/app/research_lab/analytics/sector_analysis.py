import pandas as pd
from typing import Dict, Any, List
import json
from pathlib import Path

class SectorAnalysis:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.universe_path = Path("data/universe/nifty_750_metadata.json")
        self.sector_map = self._load_sector_map()
        
    def _load_sector_map(self) -> Dict[str, str]:
        if not self.universe_path.exists():
            return {}
        with open(self.universe_path, "r") as f:
            data = json.load(f)
            return {item["Symbol"]: item.get("Sector", "Unknown") for item in data}

    def analyze_sectors(self, df: pd.DataFrame, threshold: float = 65.0) -> List[Dict[str, Any]]:
        # df index is likely (Date, Symbol) or symbol is a column
        symbols = None
        if "symbol" in df.columns:
            symbols = df["symbol"]
        elif "Symbol" in df.columns:
            symbols = df["Symbol"]
        elif isinstance(df.index, pd.MultiIndex) and "Symbol" in df.index.names:
            symbols = df.index.get_level_values("Symbol")
        elif isinstance(df.index, pd.MultiIndex) and "symbol" in df.index.names:
            symbols = df.index.get_level_values("symbol")
            
        if symbols is None:
            return [{"error": "Cannot identify symbols for sector mapping."}]
            
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
            "symbol": symbols,
            "actual": actual.values,
            "predicted": predicted.values
        })
        
        # Map sectors
        temp["sector"] = temp["symbol"].map(lambda x: self.sector_map.get(x, "Unknown"))
        
        # Calculate accuracy per sector
        results = []
        for sector, group in temp.groupby("sector"):
            tp = int((group["actual"] & group["predicted"]).sum())
            fp = int((~group["actual"] & group["predicted"]).sum())
            fn = int((group["actual"] & ~group["predicted"]).sum())
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            
            if (tp + fp) > 0: # Only care about sectors where we actually generated a signal
                results.append({
                    "sector": sector,
                    "signals_generated": int(tp + fp),
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "win_rate": round(precision, 4)
                })
                
        # Sort by Win Rate (Precision)
        results.sort(key=lambda x: x["win_rate"], reverse=True)
        return results
