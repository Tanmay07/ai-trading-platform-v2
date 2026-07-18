import yaml
import logging
from typing import List, Dict, Any

from portfolio.engine.portfolio_optimizer import PortfolioOptimizer
from portfolio.constraints.portfolio_constraints import MaxPositionsConstraint, MaxSectorExposureConstraint, CorrelationConstraint
from portfolio.correlation.correlation_engine import CorrelationEngine
from portfolio.allocation.capital_allocator import CapitalAllocator
from portfolio.analytics.portfolio_metrics import PortfolioMetrics

logger = logging.getLogger("PortfolioBuilder")

class PortfolioBuilder:
    def __init__(self):
        with open("config/portfolio_rules.yaml", "r") as f:
            self.config = yaml.safe_load(f)["portfolio"]
            
        self.correlation_engine = CorrelationEngine()
        
        # Initialize Constraints based on config
        self.constraints = [
            MaxPositionsConstraint(self.config.get("max_positions", 15)),
            MaxSectorExposureConstraint(self.config.get("max_sector_exposure", 0.25)),
            CorrelationConstraint(self.config.get("correlation_threshold", 0.85), self.correlation_engine)
        ]
        
        self.optimizer = PortfolioOptimizer(self.constraints)
        self.allocator = CapitalAllocator(strategy=self.config.get("allocation_strategy", "score_weighted"))
        
    def build_proposed_portfolio(self, candidate_opportunities: List[Dict[str, Any]], available_cash: float) -> Dict[str, Any]:
        """
        Takes raw candidates from the PredictionService and constructs a fully diversified,
        capital-aware portfolio.
        """
        logger.info(f"Building portfolio from {len(candidate_opportunities)} candidates with ${available_cash:,.2f} cash.")
        
        # 1. Optimize (Select & Reject based on constraints)
        selected, rejected = self.optimizer.optimize(candidate_opportunities)
        
        # 2. Allocate Capital
        max_weight = self.config.get("max_stock_weight", 0.15)
        allocated_portfolio = self.allocator.allocate(selected, available_cash, max_weight)
        
        # 3. Generate Analytics
        health_score = PortfolioMetrics.calculate_health_score(allocated_portfolio, rejected)
        sector_exposure = PortfolioMetrics.get_sector_exposure(allocated_portfolio)
        
        total_allocated = sum(p.get("capital_allocated", 0) for p in allocated_portfolio)
        cash_remaining = available_cash - total_allocated
        
        return {
            "status": "success",
            "metrics": {
                "health_score": round(health_score, 1),
                "total_allocated": total_allocated,
                "cash_remaining": cash_remaining,
                "sector_exposure": sector_exposure,
                "positions_count": len(allocated_portfolio)
            },
            "portfolio": allocated_portfolio,
            "rejected_candidates": rejected
        }
        
    def analyze_existing_portfolio(self, current_holdings: List[Dict[str, Any]], predictions: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates existing holdings. Recommends Hold/Reduce/Exit based on latest predictions and rules.
        (Basic prototype for Phase 7)
        """
        recommendations = []
        for holding in current_holdings:
            symbol = holding['symbol']
            pred = predictions.get(symbol, {})
            tq = pred.get('trade_quality_prediction', 0)
            
            if tq < 40:
                rec = "Exit"
                reason = f"Trade Quality has degraded significantly ({tq:.1f})"
            elif tq < 60:
                rec = "Reduce"
                reason = "Opportunity quality is marginal."
            else:
                rec = "Hold"
                reason = "Strong predicted quality."
                
            recommendations.append({
                "symbol": symbol,
                "current_weight": holding.get("weight", 0),
                "recommendation": rec,
                "reason": reason,
                "latest_trade_quality": tq
            })
            
        return recommendations
