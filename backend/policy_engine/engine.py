import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from decision_engine.models import DecisionCategory, RecommendationObject
from decision_engine.intelligence.technical import TechnicalIntelligence
from decision_engine.intelligence.valuation import ValuationIntelligence
from decision_engine.intelligence.context import PortfolioContextIntelligence
from decision_engine.intelligence.risk import RiskIntelligence
from decision_engine.explainer import DecisionExplainer

from policy_engine.models import PolicyVersion, DecisionAuditLog
from policy_engine.methodologies import MethodologyEngine

logger = logging.getLogger(__name__)

class DecisionPolicyEngine:
    def __init__(self, portfolio_service, market_data_service, db: Session):
        self.portfolio_service = portfolio_service
        self.mds = market_data_service
        self.db = db
        
        self.tech_engine = TechnicalIntelligence(self.mds)
        self.val_engine = ValuationIntelligence()
        self.ctx_engine = PortfolioContextIntelligence(self.portfolio_service)
        self.risk_engine = RiskIntelligence()
        self.explainer = DecisionExplainer()
        self.methodology = MethodologyEngine()

    def _determine_decision(self, score: float, thresholds: Dict[str, float]) -> DecisionCategory:
        if score >= thresholds.get('strong_buy', 90.0): return DecisionCategory.STRONG_BUY
        if score >= thresholds.get('buy', 80.0): return DecisionCategory.BUY_MORE
        if score >= thresholds.get('accumulate', 65.0): return DecisionCategory.ACCUMULATE
        if score >= thresholds.get('hold', 50.0): return DecisionCategory.HOLD
        if score >= thresholds.get('watch', 40.0): return DecisionCategory.WATCH
        if score >= thresholds.get('trim', 30.0): return DecisionCategory.TRIM_POSITION
        if score >= thresholds.get('sell', 20.0): return DecisionCategory.SELL
        return DecisionCategory.EXIT_IMMEDIATELY

    def execute_policy(
        self, 
        symbol: str, 
        portfolio_id: int, 
        user_id: str, 
        current_price: float, 
        policy_version: PolicyVersion
    ) -> RecommendationObject:
        """
        Executes a specific versioned policy against a stock, decoupling logic from code.
        """
        
        # 1. Gather Inputs
        tech = self.tech_engine.analyze(symbol)
        val = self.val_engine.analyze(symbol)
        ctx = self.ctx_engine.analyze(symbol, portfolio_id, user_id)
        risk = self.risk_engine.analyze(symbol)
        
        # 2. Extract Config
        weights = policy_version.weights or {"technical": 25, "valuation": 25, "context": 25, "risk": 25}
        thresholds = policy_version.thresholds or {"strong_buy": 90}
        
        # 3. Dynamic Weighted Scoring
        final_score = (
            (tech['score'] * (weights.get('technical', 25) / 100.0)) +
            (val['score'] * (weights.get('valuation', 25) / 100.0)) +
            (ctx['score'] * (weights.get('context', 25) / 100.0)) +
            (risk['score'] * (weights.get('risk', 25) / 100.0))
        )
        
        # 4. Determine Threshold Category
        decision = self._determine_decision(final_score, thresholds)
        
        # 5. Methodologies
        targets = self.methodology.calculate_targets(current_price, risk['metrics']['volatility_pct'], policy_version.target_logic or {})
        stop_loss = self.methodology.calculate_stop_loss(current_price, risk['metrics']['volatility_pct'], policy_version.stop_loss_logic or {})
        
        # 6. Explanability
        explanations = self.explainer.explain(decision.value, tech, val, ctx, risk)
        
        # Prefix the policy attribution
        policy_name = policy_version.policy.name if policy_version.policy else "Unknown Policy"
        full_why = f"[{policy_name} v{policy_version.version_number}] {explanations['explanation_why']}"
        
        # 7. Create Audit Log
        audit = DecisionAuditLog(
            portfolio_id=portfolio_id,
            symbol=symbol,
            policy_version_id=policy_version.id,
            market_data_snapshot={"tech": tech['metrics'], "val": val['metrics'], "risk": risk['metrics'], "price": current_price},
            portfolio_context_snapshot=ctx['metrics'],
            scores_breakdown={
                "tech_score": tech['score'],
                "val_score": val['score'],
                "ctx_score": ctx['score'],
                "risk_score": risk['score'],
                "final_score": final_score,
                "weights_used": weights
            },
            decision=decision.value,
            confidence=final_score,
            target_price_1=targets['target_1'],
            stop_loss=stop_loss,
            explanation=full_why
        )
        self.db.add(audit)
        self.db.commit()
        
        # 8. Return RecommendationObject (Legacy compat)
        return RecommendationObject(
            symbol=symbol,
            decision=decision,
            confidence=final_score,
            target_price_1=targets['target_1'],
            target_price_2=targets['target_2'],
            stop_loss=stop_loss,
            expected_holding_period="Varies by Policy",
            expected_cagr=targets['cagr'],
            risk_level=risk['metrics']['risk_profile'],
            position_size_recommendation=policy_version.sizing_rules.get("max_allocation", 10.0) if policy_version.sizing_rules else 10.0,
            last_review=datetime.utcnow(),
            next_review_trigger="Policy Trigger",
            
            technical_score=tech['score'],
            valuation_score=val['score'],
            portfolio_context_score=ctx['score'],
            risk_score=risk['score'],
            
            explanation_why=full_why,
            explanation_why_now=explanations['explanation_why_now'],
            explanation_metrics_changed="N/A",
            explanation_supports_view=f"Policy Weights Applied",
            explanation_risks=explanations['explanation_risks'],
            explanation_invalidation="Policy Methodologies breached"
        )
