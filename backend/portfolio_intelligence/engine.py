import logging
from typing import Dict, List
from .optimizer import PortfolioOptimizer
from .risk_manager import RiskManager
from .scenario_analyzer import ScenarioAnalyzer
from .rebalancing_advisor import RebalancingAdvisor
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio
from adaptive_learning.recommendations.recommendation_engine import RecommendationEngine

logger = logging.getLogger("PortfolioIntelligenceEngine")

class PortfolioIntelligenceEngine:
    """
    Central orchestrator for G7.5.
    Combines AI predictions with risk-aware portfolio construction.
    """
    def __init__(self):
        self.optimizer = PortfolioOptimizer()
        self.risk_manager = RiskManager()
        self.analyzer = ScenarioAnalyzer()
        self.advisor = RebalancingAdvisor()
        
    def generate_daily_workspace(self) -> Dict:
        """
        Compiles the daily decision support payload.
        """
        portfolio = VirtualPortfolio()
        port_summary = portfolio.get_portfolio_summary()
        
        cash = port_summary.get('cash_balance', 0.0)
        total_val = port_summary.get('total_value', 0.0)
        positions = port_summary.get('open_positions', [])
        
        # Get raw AI recs
        rec_engine = RecommendationEngine()
        raw_recs = rec_engine.generate_daily_recommendations(top_k=5)
        
        # Enrich recs with sizing and portfolio impact
        enriched_recs = []
        for rec in raw_recs:
            # 1. Sizing
            sizing = self.optimizer.calculate_position_size(rec, cash, total_val)
            rec.update(sizing)
            
            # 2. Impact via Scenario simulation
            if sizing['suggested_investment'] > 0:
                impact = self.analyzer.simulate_trade(
                    positions, cash, rec['symbol'], sizing['suggested_investment'], 'BUY'
                )
                rec['portfolio_impact'] = impact['deltas']
            else:
                rec['portfolio_impact'] = {"volatility": 0, "var_95": 0, "diversification": 0}
                
            enriched_recs.append(rec)
            
        # Calculate overall risk
        risk_metrics = self.risk_manager.calculate_portfolio_risk(positions, total_val)
        
        # Rebalancing plan
        rebalancing = self.advisor.generate_plan(positions, total_val)
        
        return {
            "portfolio": port_summary,
            "risk_analytics": risk_metrics,
            "recommendations": enriched_recs,
            "rebalancing_plan": rebalancing
        }
