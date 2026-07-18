import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("TradeAnalyzer")

class TradeAnalyzer:
    def __init__(self, repo_dir: str = "data/feedback_repo/"):
        self.repo_dir = repo_dir
        
    def load_feedback_records(self) -> List[Dict[str, Any]]:
        records = []
        if not os.path.exists(self.repo_dir):
            return records
            
        for filename in os.listdir(self.repo_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.repo_dir, filename)
                try:
                    with open(path, "r") as f:
                        records.append(json.load(f))
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
        return records
        
    def analyze_performance(self) -> Dict[str, Any]:
        records = self.load_feedback_records()
        total_trades = len(records)
        
        if total_trades == 0:
            return {"status": "NO_DATA"}
            
        winners = [r for r in records if r.get("trade_outcome", {}).get("is_winner")]
        losers = [r for r in records if not r.get("trade_outcome", {}).get("is_winner")]
        
        win_rate = len(winners) / total_trades
        gross_profit = sum(r["trade_outcome"]["pnl"] for r in winners)
        gross_loss = abs(sum(r["trade_outcome"]["pnl"] for r in losers))
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Attribution Aggregation
        pred_attr = sum(r.get("attribution", {}).get("prediction_layer", 0) for r in records)
        exec_attr = sum(r.get("attribution", {}).get("execution_layer", 0) for r in records)
        port_attr = sum(r.get("attribution", {}).get("portfolio_layer", 0) for r in records)
        
        return {
            "status": "OK",
            "total_trades_analyzed": total_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "subsystem_attribution": {
                "prediction": pred_attr,
                "execution": exec_attr,
                "portfolio": port_attr
            },
            "records": records
        }
