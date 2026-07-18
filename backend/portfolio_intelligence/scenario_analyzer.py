import logging
from typing import Dict, List
import copy
from .risk_manager import RiskManager

logger = logging.getLogger("ScenarioAnalyzer")

class ScenarioAnalyzer:
    """
    Evaluates what-if scenarios on the portfolio.
    """
    def __init__(self):
        self.risk_manager = RiskManager()
        
    def simulate_trade(self, current_positions: List[Dict], current_cash: float, trade_symbol: str, trade_amount: float, action: str = 'BUY') -> Dict:
        """
        Action: 'BUY' or 'SELL'.
        Amount: Dollar value.
        """
        total_val = current_cash + sum(p['quantity'] * p['entry_price'] for p in current_positions)
        
        # Calculate baseline metrics
        baseline = self.risk_manager.calculate_portfolio_risk(current_positions, total_val)
        
        # Create hypothetical state
        hypo_positions = copy.deepcopy(current_positions)
        hypo_cash = current_cash
        
        if action == 'BUY':
            if trade_amount > current_cash:
                raise ValueError("Insufficient cash for scenario")
            hypo_cash -= trade_amount
            
            # See if we already hold it
            existing = next((p for p in hypo_positions if p['symbol'] == trade_symbol), None)
            if existing:
                # Simplified blending
                total_invested = (existing['quantity'] * existing['entry_price']) + trade_amount
                new_price = existing['entry_price'] # Assume same price for simplicity
                existing['quantity'] = total_invested / new_price
            else:
                # Assume 1 unit = $1 for prototype math simplicity
                hypo_positions.append({
                    "symbol": trade_symbol,
                    "entry_price": 100.0,
                    "quantity": trade_amount / 100.0,
                    "ai_confidence": 0.75 # assumed high conviction for buy
                })
        elif action == 'SELL':
            existing = next((p for p in hypo_positions if p['symbol'] == trade_symbol), None)
            if not existing:
                raise ValueError("Position not found")
            
            current_invested = existing['quantity'] * existing['entry_price']
            if trade_amount >= current_invested:
                hypo_positions.remove(existing)
                hypo_cash += current_invested
            else:
                ratio = (current_invested - trade_amount) / current_invested
                existing['quantity'] *= ratio
                hypo_cash += trade_amount
                
        # Calculate hypothetical metrics
        hypo = self.risk_manager.calculate_portfolio_risk(hypo_positions, total_val)
        
        # Compute deltas
        return {
            "baseline": baseline,
            "hypothetical": hypo,
            "deltas": {
                "volatility": hypo["portfolio_volatility"] - baseline["portfolio_volatility"],
                "var_95": hypo["value_at_risk_95"] - baseline["value_at_risk_95"],
                "diversification": hypo["diversification_score"] - baseline["diversification_score"]
            }
        }
