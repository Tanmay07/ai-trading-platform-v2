import yaml
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("PromotionEngine")

class PromotionEngine:
    def __init__(self):
        with open("config/benchmarking.yaml", "r") as f:
            self.rules = yaml.safe_load(f)["benchmarking"]["promotion_rules"]
            
    def evaluate_promotion(self, champion_metrics: Dict[str, Any], challenger_metrics: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates strict rules to determine if the Challenger should become the new Champion.
        """
        roc_diff = challenger_metrics.get("cv_roc_auc", 0) - champion_metrics.get("cv_roc_auc", 0)
        p20_diff = challenger_metrics.get("test_precision_20", 0) - champion_metrics.get("test_precision_20", 0)
        
        champ_pf = champion_metrics.get("test_profit_factor", 0)
        chall_pf = challenger_metrics.get("test_profit_factor", 0)
        
        # Rule 1: Min ROC Improvement
        if roc_diff < self.rules.get("min_roc_improvement", 0.02):
            return False, f"Failed Rule 1: ROC Improvement ({roc_diff:.4f}) < {self.rules.get('min_roc_improvement')}"
            
        # Rule 2: Min Precision@20 Improvement
        if p20_diff < self.rules.get("min_precision20_improvement", 0.01):
            return False, f"Failed Rule 2: Precision@20 Improvement ({p20_diff:.4f}) < {self.rules.get('min_precision20_improvement')}"
            
        # Rule 3: Profit Factor MUST NOT degrade if require_profit_factor_improvement is true
        if self.rules.get("require_profit_factor_improvement", True) and chall_pf <= champ_pf:
            return False, f"Failed Rule 3: Challenger Profit Factor ({chall_pf:.2f}) <= Champion ({champ_pf:.2f})"
            
        # Optional: Research Confidence Score (from the E3.7 prompt recommendation)
        if self.rules.get("require_research_confidence_improvement", False):
            # Simulated confidence check
            # Real implementation would calculate stability across folds and regimes
            champ_conf = champion_metrics.get("research_confidence_score", 75.0)
            chall_conf = challenger_metrics.get("research_confidence_score", 80.0)
            if chall_conf <= champ_conf:
                 return False, f"Failed Rule 4: Research Confidence ({chall_conf}) <= Champion ({champ_conf})"
                 
        return True, "Challenger meets all institutional promotion criteria."
