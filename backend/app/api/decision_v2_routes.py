from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from decision_engine.database import get_db, AlertRecord
from policy_engine.engine import DecisionPolicyEngine
from decision_engine.models import RecommendationObject
from decision_engine.scanner import OpportunityScanner
from decision_engine.rebalancer import PortfolioRebalancer
from portfolio_manager.portfolio_service import PortfolioService
from portfolio_manager.database import get_db as get_portfolio_db
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider
from app.infrastructure.auth.jwt_auth import get_current_user

from policy_engine.database import get_db as get_policy_db
from policy_engine.models import Policy, PolicyVersion

router = APIRouter()

def get_policy_engine(portfolio_db: Session = Depends(get_portfolio_db), policy_db: Session = Depends(get_policy_db)):
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    return DecisionPolicyEngine(portfolio_service, mds, policy_db)

def get_active_policy(policy_id: Optional[int], policy_db: Session) -> PolicyVersion:
    """Helper to fetch the requested policy or fallback to a default mock policy if none exists."""
    if policy_id:
        policy = policy_db.query(Policy).filter(Policy.id == policy_id).first()
        if policy and policy.active_version_id:
            return policy_db.query(PolicyVersion).filter(PolicyVersion.id == policy.active_version_id).first()
            
    # Mocking a fallback if no DB policies exist yet
    return PolicyVersion(
        weights={"technical": 30, "valuation": 30, "context": 20, "risk": 20},
        thresholds={"strong_buy": 90, "buy": 80, "accumulate": 65, "hold": 50, "watch": 40, "trim": 30, "sell": 20},
        target_logic={"methodology": "RISK_REWARD"},
        stop_loss_logic={"methodology": "PERCENTAGE", "params": {"percentage": 10.0}}
    )

@router.get("/recommendations/{portfolio_id}", response_model=List[RecommendationObject])
def get_portfolio_recommendations(
    portfolio_id: int,
    policy_id: Optional[int] = None,
    user: dict = Depends(get_current_user),
    engine: DecisionPolicyEngine = Depends(get_policy_engine),
    portfolio_db: Session = Depends(get_portfolio_db),
    policy_db: Session = Depends(get_policy_db)
):
    """
    Generates recommendations for all current holdings in the portfolio based on the selected Policy.
    """
    active_policy_version = get_active_policy(policy_id, policy_db)
    
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    holdings = portfolio_service.get_holdings(portfolio_id, user["user_id"])
    
    recommendations = []
    for h in holdings:
        rec = engine.execute_policy(h.symbol, portfolio_id, user["user_id"], h.current_price or 1000.0, active_policy_version)
        recommendations.append(rec)
        
    return recommendations

@router.get("/recommendations/{portfolio_id}/{symbol}", response_model=RecommendationObject)
def get_symbol_recommendation(
    portfolio_id: int,
    symbol: str,
    policy_id: Optional[int] = None,
    user: dict = Depends(get_current_user),
    engine: DecisionPolicyEngine = Depends(get_policy_engine),
    policy_db: Session = Depends(get_policy_db)
):
    active_policy_version = get_active_policy(policy_id, policy_db)
    return engine.execute_policy(symbol.upper(), portfolio_id, user["user_id"], 1000.0, active_policy_version)

@router.get("/opportunities/{portfolio_id}", response_model=List[Dict[str, Any]])
def get_opportunities(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    decision_db: Session = Depends(get_db)
):
    from decision_engine.database import OpportunityRecord
    records = decision_db.query(OpportunityRecord).order_by(OpportunityRecord.confidence.desc()).limit(50).all()
    return [
        {
            "symbol": r.symbol, "decision": r.decision, "confidence": r.confidence,
            "target_price_1": r.target_price_1, "expected_cagr": r.expected_cagr,
            "reason": r.reason, "scanned_at": r.scanned_at
        } for r in records
    ]

@router.post("/opportunities/scan/{portfolio_id}")
def trigger_scan(
    portfolio_id: int,
    policy_id: Optional[int] = None,
    user: dict = Depends(get_current_user),
    engine: DecisionPolicyEngine = Depends(get_policy_engine),
    decision_db: Session = Depends(get_db),
    policy_db: Session = Depends(get_policy_db)
):
    active_policy_version = get_active_policy(policy_id, policy_db)
    scanner = OpportunityScanner(engine, active_policy_version)
    scanner.run_background_scan(decision_db, portfolio_id, user["user_id"])
    return {"message": "Nifty 750 Scan Complete. Opportunities updated."}

@router.get("/rebalancing/{portfolio_id}", response_model=Dict[str, Any])
def get_rebalancing_suggestions(
    portfolio_id: int,
    policy_id: Optional[int] = None,
    user: dict = Depends(get_current_user),
    engine: DecisionPolicyEngine = Depends(get_policy_engine),
    portfolio_db: Session = Depends(get_portfolio_db),
    policy_db: Session = Depends(get_policy_db)
):
    active_policy_version = get_active_policy(policy_id, policy_db)
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    holdings = portfolio_service.get_holdings(portfolio_id, user["user_id"])
    
    recs = [engine.execute_policy(h.symbol, portfolio_id, user["user_id"], h.current_price or 1000.0, active_policy_version) for h in holdings]
    
    rebalancer = PortfolioRebalancer()
    return rebalancer.generate_suggestions(recs)

@router.get("/alerts", response_model=List[Dict[str, Any]])
def get_alerts(
    user: dict = Depends(get_current_user),
    decision_db: Session = Depends(get_db)
):
    alerts = decision_db.query(AlertRecord).filter(AlertRecord.user_id == user["user_id"]).order_by(AlertRecord.created_at.desc()).limit(50).all()
    return [{"id": a.id, "symbol": a.symbol, "type": a.alert_type, "message": a.message, "date": a.created_at} for a in alerts]

@router.get("/health/recommendation-engine")
def get_health():
    return {"status": "ok", "message": "Investment Decision Policy Engine is operational."}
