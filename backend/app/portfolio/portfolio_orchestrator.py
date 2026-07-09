from typing import Dict, Any, List
from app.portfolio.correlation_engine import CorrelationEngine
from app.portfolio.diversification_engine import DiversificationEngine
from app.portfolio.allocation_engine import AllocationEngine
from app.portfolio.portfolio_optimizer import PortfolioOptimizer
from app.portfolio.portfolio_registry import PortfolioRegistry

class PortfolioOrchestrator:
    def __init__(self):
        self.registry = PortfolioRegistry()
        self.correlation = CorrelationEngine()
        self.diversification = DiversificationEngine()
        self.allocation = AllocationEngine()
        self.optimizer = PortfolioOptimizer()
        
    def filter_and_allocate(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw recommendations, filters by portfolio constraints, and sizes them.
        """
        current_portfolio = self.registry.get_latest_snapshot()
        
        valid_candidates = []
        for cand in candidates:
            ticker = cand.get("Ticker")
            sector = cand.get("Sector")
            
            # 1. Correlation Check
            corr = self.correlation.calculate_correlation_impact(current_portfolio, ticker)
            if not self.correlation.is_acceptable(corr):
                cand["Rejected_Reason"] = f"Correlation too high: {corr}"
                continue
                
            # 2. Diversification Check
            div_score = self.diversification.evaluate_impact(current_portfolio, sector)
            
            # 3. Size Position
            alloc = self.allocation.allocate(current_portfolio, cand)
            if alloc["final_allocation_cash"] <= 0:
                cand["Rejected_Reason"] = "Zero allocation allowed due to exposure limits"
                continue
                
            cand["Portfolio_Fit_Score"] = round((cand.get("Confidence", 50) + div_score * 100) / 2, 1)
            cand["Portfolio_Correlation_Impact"] = corr
            cand["Diversification_Impact"] = div_score
            cand["Kelly_Fraction"] = alloc["kelly_fraction"]
            cand["Recommended_Allocation_Pct"] = alloc["final_allocation_pct"]
            cand["Recommended_Allocation_Cash"] = alloc["final_allocation_cash"]
            
            valid_candidates.append(cand)
            
        # 4. Global Optimization
        optimized_candidates = self.optimizer.optimize(current_portfolio, valid_candidates)
        return optimized_candidates
