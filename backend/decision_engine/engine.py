from datetime import datetime
from typing import Dict, Any

from decision_engine.config import config
from decision_engine.models import DecisionCategory, RecommendationObject
from decision_engine.intelligence.technical import TechnicalIntelligence
from decision_engine.intelligence.valuation import ValuationIntelligence
from decision_engine.intelligence.context import PortfolioContextIntelligence
from decision_engine.intelligence.risk import RiskIntelligence
from decision_engine.explainer import DecisionExplainer
from decision_engine.targets import TargetEngine

class InvestmentDecisionEngine:
    def __init__(self, portfolio_service, market_data_service):
        self.portfolio_service = portfolio_service
        self.mds = market_data_service
        
        self.tech_engine = TechnicalIntelligence(self.mds)
        self.val_engine = ValuationIntelligence()
        self.ctx_engine = PortfolioContextIntelligence(self.portfolio_service)
        self.risk_engine = RiskIntelligence()
        
        self.explainer = DecisionExplainer()
        self.target_engine = TargetEngine()

    def analyze_holding(self, symbol: str, portfolio_id: int, user_id: str, current_price: float) -> RecommendationObject:
        """
        Analyzes a stock and generates an explainable Recommendation Object.
        """
        # 1. Gather Intelligence
        tech = self.tech_engine.analyze(symbol)
        val = self.val_engine.analyze(symbol)
        ctx = self.ctx_engine.analyze(symbol, portfolio_id, user_id)
        risk = self.risk_engine.analyze(symbol)
        
        # 2. Compute Weighted Score (0-100)
        final_score = (
            (tech['score'] * config.WEIGHT_TECHNICAL) +
            (val['score'] * config.WEIGHT_VALUATION) +
            (ctx['score'] * config.WEIGHT_CONTEXT) +
            (risk['score'] * config.WEIGHT_RISK)
        )
        
        # 3. Determine Category
        decision = DecisionCategory.HOLD
        if final_score >= config.STRONG_BUY_THRESHOLD: decision = DecisionCategory.STRONG_BUY
        elif final_score >= config.BUY_THRESHOLD: decision = DecisionCategory.BUY_MORE
        elif final_score >= config.ACCUMULATE_THRESHOLD: decision = DecisionCategory.ACCUMULATE
        elif final_score >= config.HOLD_THRESHOLD: decision = DecisionCategory.HOLD
        elif final_score >= config.SELL_THRESHOLD: decision = DecisionCategory.TRIM_POSITION
        elif final_score >= config.EXIT_IMMEDIATELY_THRESHOLD: decision = DecisionCategory.SELL
        else: decision = DecisionCategory.EXIT_IMMEDIATELY
            
        # 4. Generate Explanations
        explanations = self.explainer.explain(decision.value, tech, val, ctx, risk)
        
        # 5. Generate Targets
        targets = self.target_engine.calculate_targets(current_price, risk['metrics']['volatility_pct'], val['metrics']['valuation_status'])
        
        return RecommendationObject(
            symbol=symbol,
            decision=decision,
            confidence=final_score, # For simplicity, score maps to confidence
            target_price_1=targets['target_1'],
            target_price_2=targets['target_2'],
            stop_loss=targets['stop_loss'],
            expected_holding_period="12-18 Months" if decision in [DecisionCategory.STRONG_BUY, DecisionCategory.BUY_MORE] else "N/A",
            expected_cagr=targets['cagr'],
            risk_level=risk['metrics']['risk_profile'],
            position_size_recommendation=10.0 if final_score > 70 else 5.0, # Max portfolio weight 
            last_review=datetime.utcnow(),
            next_review_trigger="Earnings Date or Target/Stop Hit",
            
            technical_score=tech['score'],
            valuation_score=val['score'],
            portfolio_context_score=ctx['score'],
            risk_score=risk['score'],
            
            explanation_why=explanations['explanation_why'],
            explanation_why_now=explanations['explanation_why_now'],
            explanation_metrics_changed=explanations['explanation_metrics_changed'],
            explanation_supports_view=explanations['explanation_supports_view'],
            explanation_risks=explanations['explanation_risks'],
            explanation_invalidation=explanations['explanation_invalidation']
        )
