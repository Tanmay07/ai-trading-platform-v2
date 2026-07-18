from typing import Dict, Any, List

class RuleEngine:
    """
    Enforces hard institutional governance rules that bypass standard weighted voting.
    """
    def __init__(self, config: Dict[str, Any]):
        self.rules = config.get("rules", {})
        
    def validate(self, trade_context: Dict[str, Any]) -> List[str]:
        """
        Returns a list of veto reasons. If empty, the trade passes rule validation.
        """
        vetos = []
        
        if self.rules.get("enforce_rr_validation", True):
             rr = trade_context.get("execution", {}).get("risk_reward", 0.0)
             if rr < 2.0:
                 vetos.append(f"Hard Governance Veto: Risk/Reward ({rr}) is below absolute minimum of 2.0")
                 
        if self.rules.get("enforce_sector_limits", True):
             portfolio = trade_context.get("portfolio", {})
             if portfolio.get("is_rejected", False):
                 vetos.append(f"Hard Governance Veto: Portfolio constraint violations ({portfolio.get('rejection_reasons', [])})")
                 
        return vetos
