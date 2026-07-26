from typing import Dict, Any

class PortfolioContextIntelligence:
    def __init__(self, portfolio_service):
        self.portfolio_service = portfolio_service

    def analyze(self, symbol: str, portfolio_id: int, user_id: str) -> Dict[str, Any]:
        """
        Analyzes the stock against the current portfolio holdings.
        Penalizes over-concentration.
        """
        try:
            holdings = self.portfolio_service.get_holdings(portfolio_id, user_id)
            total_value = sum(h.current_value for h in holdings if h.current_value)
            
            # Find current allocation
            current_weight = 0.0
            for h in holdings:
                if h.symbol == symbol and h.current_value:
                    current_weight = (h.current_value / total_value) * 100 if total_value > 0 else 0.0
                    break
                    
            score = 100.0
            
            # Concentration Penalty
            if current_weight > 25.0:
                score -= 80 # Extreme penalty, should almost force a SELL or TRIM
            elif current_weight > 15.0:
                score -= 40 # Moderate penalty, prevents BUY MORE
            elif current_weight > 10.0:
                score -= 20
                
            return {
                "score": max(0.0, score),
                "metrics": {
                    "current_weight_pct": round(current_weight, 2),
                    "is_concentrated": current_weight > 15.0,
                    "target_max_weight_pct": 10.0
                }
            }
            
        except Exception:
            return {
                "score": 50.0,
                "metrics": {
                    "current_weight_pct": 0.0,
                    "is_concentrated": False,
                    "target_max_weight_pct": 10.0
                }
            }
