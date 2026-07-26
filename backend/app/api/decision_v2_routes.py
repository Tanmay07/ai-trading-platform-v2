from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from decision_engine.database import get_db, AlertRecord
from decision_engine.engine import InvestmentDecisionEngine
from decision_engine.models import RecommendationObject
from decision_engine.scanner import OpportunityScanner
from decision_engine.rebalancer import PortfolioRebalancer
from portfolio_manager.portfolio_service import PortfolioService
from portfolio_manager.database import get_db as get_portfolio_db
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider
from app.infrastructure.auth.jwt_auth import get_current_user

router = APIRouter()

def get_engine(portfolio_db: Session = Depends(get_portfolio_db)):
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    return InvestmentDecisionEngine(portfolio_service, mds)

@router.get("/recommendations/{portfolio_id}", response_model=List[RecommendationObject])
def get_portfolio_recommendations(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    engine: InvestmentDecisionEngine = Depends(get_engine),
    portfolio_db: Session = Depends(get_portfolio_db)
):
    """
    Generates recommendations for all current holdings in the portfolio.
    """
    # Get current holdings
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    holdings = portfolio_service.get_holdings(portfolio_id, user["user_id"])
    
    recommendations = []
    for h in holdings:
        rec = engine.analyze_holding(h.symbol, portfolio_id, user["user_id"], h.current_price or 1000.0)
        recommendations.append(rec)
        
    return recommendations

@router.get("/recommendations/{portfolio_id}/{symbol}", response_model=RecommendationObject)
def get_symbol_recommendation(
    portfolio_id: int,
    symbol: str,
    user: dict = Depends(get_current_user),
    engine: InvestmentDecisionEngine = Depends(get_engine)
):
    """
    Generate recommendation for a specific symbol.
    """
    # Mocking price for now, ideally fetch from MDS
    return engine.analyze_holding(symbol.upper(), portfolio_id, user["user_id"], 1000.0)

@router.get("/opportunities/{portfolio_id}", response_model=List[Dict[str, Any]])
def get_opportunities(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    decision_db: Session = Depends(get_db)
):
    """
    Returns high conviction buys from the latest Nifty 750 background scan.
    """
    from decision_engine.database import OpportunityRecord
    records = decision_db.query(OpportunityRecord).order_by(OpportunityRecord.confidence.desc()).limit(50).all()
    return [
        {
            "symbol": r.symbol,
            "decision": r.decision,
            "confidence": r.confidence,
            "target_price_1": r.target_price_1,
            "expected_cagr": r.expected_cagr,
            "reason": r.reason,
            "scanned_at": r.scanned_at
        } for r in records
    ]

@router.post("/opportunities/scan/{portfolio_id}")
def trigger_scan(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    engine: InvestmentDecisionEngine = Depends(get_engine),
    decision_db: Session = Depends(get_db)
):
    """
    Triggers a synchronous background scan (in a real production app this queues a Celery job).
    For Phase P3, we run it directly here to populate the DB.
    """
    scanner = OpportunityScanner(engine)
    scanner.run_background_scan(decision_db, portfolio_id, user["user_id"])
    return {"message": "Nifty 750 Scan Complete. Opportunities updated."}

@router.get("/rebalancing/{portfolio_id}", response_model=Dict[str, Any])
def get_rebalancing_suggestions(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    engine: InvestmentDecisionEngine = Depends(get_engine),
    portfolio_db: Session = Depends(get_portfolio_db)
):
    # Fetch recommendations for holdings
    mds = MarketDataService(JugaadProvider())
    portfolio_service = PortfolioService(portfolio_db, mds)
    holdings = portfolio_service.get_holdings(portfolio_id, user["user_id"])
    
    recs = [engine.analyze_holding(h.symbol, portfolio_id, user["user_id"], h.current_price or 1000.0) for h in holdings]
    
    rebalancer = PortfolioRebalancer()
    return rebalancer.generate_suggestions(recs)

@router.get("/alerts", response_model=List[Dict[str, Any]])
def get_alerts(
    user: dict = Depends(get_current_user),
    decision_db: Session = Depends(get_db)
):
    """
    Fetches DB alerts.
    """
    alerts = decision_db.query(AlertRecord).filter(AlertRecord.user_id == user["user_id"]).order_by(AlertRecord.created_at.desc()).limit(50).all()
    return [{"id": a.id, "symbol": a.symbol, "type": a.alert_type, "message": a.message, "date": a.created_at} for a in alerts]

@router.get("/health/recommendation-engine")
def get_health():
    return {"status": "ok", "message": "Investment Decision Intelligence Engine (IDIE) is operational."}
