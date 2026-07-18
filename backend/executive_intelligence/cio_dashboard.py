import logging
from typing import Dict, Any
from .portfolio_health import PortfolioHealthEngine
from .market_intelligence import MarketIntelligenceEngine
from .daily_brief import DailyBriefGenerator
from .alerts_engine import AlertsEngine
from portfolio_intelligence.engine import PortfolioIntelligenceEngine

logger = logging.getLogger("CIODashboard")

class CIODashboardEngine:
    """
    Central orchestrator for G7.6 Executive Intelligence.
    Aggregates data from Portfolio Intelligence, Market Intelligence, and Virtual Portfolio.
    """
    def __init__(self):
        self.port_intelligence = PortfolioIntelligenceEngine()
        self.health_engine = PortfolioHealthEngine()
        self.market_engine = MarketIntelligenceEngine()
        self.brief_gen = DailyBriefGenerator()
        self.alerts_engine = AlertsEngine()
        
    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Builds the unified payload for the CIO Dashboard.
        """
        # 1. Base Portfolio Intelligence
        workspace = self.port_intelligence.generate_daily_workspace()
        
        portfolio = workspace['portfolio']
        risk = workspace['risk_analytics']
        recs = workspace['recommendations']
        
        # 2. Executive Analytics
        cash_ratio = portfolio.get('cash_balance', 0) / portfolio.get('total_value', 1) if portfolio.get('total_value', 0) > 0 else 0
        health = self.health_engine.calculate_health(risk, cash_ratio)
        market = self.market_engine.get_market_snapshot()
        
        # 3. Briefs & Alerts
        brief = self.brief_gen.generate_brief(market, portfolio, recs)
        alerts = self.alerts_engine.generate_alerts(risk, health, recs)
        
        return {
            "market_snapshot": market,
            "portfolio_snapshot": portfolio,
            "portfolio_health": health,
            "risk_overview": risk,
            "recommendations": recs,
            "daily_brief": brief,
            "alerts": alerts
        }
