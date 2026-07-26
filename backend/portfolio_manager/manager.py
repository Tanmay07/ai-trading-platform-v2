import logging
from typing import List, Dict, Any
from .fundamental_engine import FundamentalEngine
from .technical_engine import TechnicalEngine
from .portfolio_context import PortfolioContextEngine
from .recommendation_engine import RecommendationEngine
from .opportunity_scanner import OpportunityScanner

logger = logging.getLogger(__name__)

class AIPortfolioManager:
    """
    Orchestrates the entire AI Portfolio analysis.
    """
    def __init__(self):
        self.fundamental = FundamentalEngine()
        self.technical = TechnicalEngine()
        self.context = PortfolioContextEngine()
        self.recommender = RecommendationEngine()
        self.scanner = OpportunityScanner()
        
    def analyze_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs full analysis on the provided holdings.
        """
        logger.info("AIPortfolioManager starting full portfolio analysis.")
        
        # 1. Analyze Context
        context_data = self.context.analyze(holdings)
        
        enriched_holdings = []
        
        total_value = context_data.get("total_value", 0)
        
        for holding in holdings:
            symbol = holding.get("symbol")
            cp = holding.get("current_price", 0)
            
            # 2. Fundamental & Technical Analysis
            f_data = self.fundamental.analyze(symbol, sector=holding.get("sector"))
            t_data = self.technical.analyze(symbol, current_price=cp)
            
            # 3. Recommendation Generation
            rec = self.recommender.generate_recommendation(
                symbol=symbol,
                fundamental=f_data,
                technical=t_data,
                context=context_data,
                current_price=cp
            )
            
            # Merge data back to holding
            enriched = {
                **holding,
                "fundamental_analysis": f_data,
                "technical_analysis": t_data,
                "recommendation": rec
            }
            
            # Calculate weight
            if total_value > 0:
                enriched["weight"] = round((holding.get("market_value", 0) / total_value) * 100, 2)
            else:
                enriched["weight"] = 0
                
            enriched_holdings.append(enriched)
            
        # 4. Scanner
        opportunities = self.scanner.scan(holdings)
        
        # Calculate aggregate metrics
        total_pnl = sum([h.get("unrealized_pnl", 0) for h in holdings])
        total_invested = sum([(h.get("avg_buy_price", 0) * h.get("quantity", 0)) for h in holdings])
        
        cagr = 12.5 # Mock CAGR
        risk_score = 65 # Mock Risk
        health_score = 82 # Mock Health
        
        return {
            "dashboard": {
                "portfolio_value": round(total_value, 2),
                "total_invested": round(total_invested, 2),
                "total_unrealized_pnl": round(total_pnl, 2),
                "absolute_return": round((total_pnl / total_invested * 100) if total_invested else 0, 2),
                "cagr": cagr,
                "risk_score": risk_score,
                "health_score": health_score,
                "holdings_count": len(holdings)
            },
            "allocations": context_data.get("allocations"),
            "sectors": context_data.get("sectors"),
            "holdings": enriched_holdings,
            "opportunities": opportunities,
            "alerts": [
                {"message": "Infosys broke 50 DMA support.", "type": "warning"},
                {"message": "Reliance reached Target Price 1.", "type": "success"}
            ]
        }
