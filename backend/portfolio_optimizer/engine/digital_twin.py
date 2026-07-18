import logging
from typing import Dict, Any

logger = logging.getLogger("PortfolioDigitalTwin")

class PortfolioDigitalTwin:
    """
    Maintains a shadow copy of the active portfolio and compares it against
    proposed optimizations to compute marginal utility and recommend rebalances.
    """
    def __init__(self):
        # MVP Mock of current active portfolio weights
        self.current_portfolio = {
            "RELIANCE.NS": 12.0,
            "TCS.NS": 8.0,
            "HDFCBANK.NS": 15.0
        }
        
    def evaluate_rebalance(self, proposed_weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates turnover and makes a recommendation.
        """
        turnover = 0.0
        
        # Calculate turnover (sum of absolute weight changes / 2)
        all_symbols = set(self.current_portfolio.keys()).union(proposed_weights.keys())
        for sym in all_symbols:
            current_w = self.current_portfolio.get(sym, 0.0)
            proposed_w = proposed_weights.get(sym, 0.0)
            turnover += abs(current_w - proposed_w)
            
        turnover_pct = round(turnover / 2.0, 2)
        
        # Estimate transaction costs (0.1% per turnover unit)
        estimated_costs = round(turnover_pct * 0.1, 2)
        
        # Dummy marginal return (for MVP just randomize a slight edge)
        marginal_return = round(turnover_pct * 0.15, 2)
        
        # Decision logic
        if turnover_pct < 5.0:
            recommendation = "DELAY_REBALANCE"
            reason = "Turnover too low to justify transaction costs."
        elif marginal_return < estimated_costs:
            recommendation = "REJECT_REBALANCE"
            reason = f"Transaction costs ({estimated_costs}%) outweigh expected marginal return ({marginal_return}%)."
        else:
            recommendation = "ACCEPT_REBALANCE"
            reason = f"Marginal return ({marginal_return}%) justifies turnover ({turnover_pct}%)."
            
        return {
            "turnover_pct": turnover_pct,
            "estimated_transaction_costs_pct": estimated_costs,
            "expected_marginal_return_pct": marginal_return,
            "recommendation": recommendation,
            "reason": reason
        }
