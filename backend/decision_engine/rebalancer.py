from typing import List, Dict, Any
from decision_engine.models import DecisionCategory

class PortfolioRebalancer:
    def generate_suggestions(self, current_holdings_recommendations: List[Any]) -> Dict[str, Any]:
        """
        Takes a list of RecommendationObjects for the current portfolio and suggests structural changes.
        """
        increase = []
        reduce = []
        exit_positions = []
        
        for rec in current_holdings_recommendations:
            if rec.decision in [DecisionCategory.STRONG_BUY, DecisionCategory.BUY_MORE, DecisionCategory.ACCUMULATE]:
                increase.append({"symbol": rec.symbol, "target_weight": rec.position_size_recommendation, "reason": rec.explanation_why})
            elif rec.decision in [DecisionCategory.TRIM_POSITION, DecisionCategory.BOOK_PARTIAL_PROFIT]:
                reduce.append({"symbol": rec.symbol, "reason": rec.explanation_why})
            elif rec.decision in [DecisionCategory.SELL, DecisionCategory.EXIT_IMMEDIATELY]:
                exit_positions.append({"symbol": rec.symbol, "reason": rec.explanation_why})
                
        return {
            "rebalance_actions": {
                "increase": increase,
                "reduce": reduce,
                "exit": exit_positions
            },
            "summary": f"Suggested to increase {len(increase)} positions, reduce {len(reduce)}, and exit {len(exit_positions)}."
        }
