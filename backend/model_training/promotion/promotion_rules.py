import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger("PromotionRules")

class PromotionRules:
    def __init__(self):
        with open("config/production_model.yaml", "r") as f:
            self.config = yaml.safe_load(f)["promotion"]
            
    def evaluate(self, champion_metrics: Dict[str, Any], challenger_metrics: Dict[str, Any]) -> tuple:
        """
        Evaluates strict trading-centric promotion rules.
        """
        if self.config.get("force_promote", False):
            return True, "Forced promotion override active (E4.1)."
            
        rules = self.config["minimum_improvements"]
        failures = []
        
        def check_improvement(metric_name, rules_key, fallback_val=0):
            champ = champion_metrics.get(metric_name, fallback_val)
            chall = challenger_metrics.get(metric_name, fallback_val)
            if champ == 0: # Avoid div by zero, assume improvement if champ is 0 and chall > 0
                 return chall > 0
            pct_improvement = (chall - champ) / abs(champ)
            req = rules.get(rules_key, 0)
            if pct_improvement < req:
                failures.append(f"{metric_name} improved by {pct_improvement*100:.1f}%, required {req*100:.1f}%")
                return False
            return True

        check_improvement("Precision@20", "precision_at_20")
        check_improvement("Profit_Factor", "profit_factor", fallback_val=1.0)
        
        # Trade quality and target hit rate might require WalkForward simulated backtest outputs
        # We will check if they exist, otherwise we fallback
        if "Average_Trade_Quality" in challenger_metrics:
            check_improvement("Average_Trade_Quality", "average_trade_quality")
            
        if "Sharpe_Ratio" in challenger_metrics:
            check_improvement("Sharpe_Ratio", "sharpe_ratio")
            
        if failures:
             return False, "Failed Promotion Criteria: " + "; ".join(failures)
             
        return True, "Passed all strict trading-centric promotion criteria."
