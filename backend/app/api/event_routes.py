from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from event_engine.database import get_db
from event_engine.models import MarketEventRecord
from event_engine.engine import EnterpriseMarketIntelligenceEngine
from event_engine.detectors.technical import TechnicalEventDetector
from event_engine.detectors.corporate import CorporateEventDetector
from event_engine.watchlists import WatchlistService
from event_engine.calendar import CalendarEngine
from app.infrastructure.auth.jwt_auth import get_current_user
from portfolio_manager.portfolio_service import PortfolioService
from portfolio_manager.database import get_db as get_portfolio_db
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider

router = APIRouter()

def get_emie(db: Session = Depends(get_db)):
    return EnterpriseMarketIntelligenceEngine(db)

@router.get("/", response_model=List[Dict[str, Any]])
def get_all_events(
    limit: int = 50, 
    type: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(MarketEventRecord).order_by(MarketEventRecord.created_at.desc())
    if type:
        query = query.filter(MarketEventRecord.type == type)
    events = query.limit(limit).all()
    
    return [
        {
            "id": e.event_id,
            "type": e.type,
            "subtype": e.subtype,
            "impact_score": e.impact_score,
            "priority": e.priority,
            "symbols": e.symbols_json,
            "timestamp": e.created_at
        } for e in events
    ]

@router.get("/portfolio", response_model=List[Dict[str, Any]])
def get_portfolio_events(
    portfolio_id: int,
    user: dict = Depends(get_current_user),
    portfolio_db: Session = Depends(get_portfolio_db),
    event_db: Session = Depends(get_db)
):
    mds = MarketDataService(JugaadProvider())
    ps = PortfolioService(portfolio_db, mds)
    holdings = ps.get_holdings(portfolio_id, user["user_id"])
    symbols = [h.symbol for h in holdings]
    
    events = event_db.query(MarketEventRecord).order_by(MarketEventRecord.created_at.desc()).limit(100).all()
    filtered = []
    for e in events:
        esyms = e.symbols_json or []
        if any(s in esyms for s in symbols):
            filtered.append({
                "id": e.event_id,
                "type": e.type,
                "subtype": e.subtype,
                "priority": e.priority,
                "symbols": e.symbols_json,
                "timestamp": e.created_at
            })
    return filtered

@router.get("/watchlist/{watchlist_name}", response_model=List[Dict[str, Any]])
def get_watchlist_events(
    watchlist_name: str,
    symbols: str = "", # comma separated
    event_db: Session = Depends(get_db)
):
    sym_list = symbols.split(",") if symbols else []
    ws = WatchlistService(event_db)
    return ws.get_watchlist_events(watchlist_name, sym_list)

@router.get("/calendar", response_model=List[Dict[str, Any]])
def get_calendar():
    ce = CalendarEngine()
    return ce.get_upcoming_events()

@router.post("/mock/technical/breakout")
async def trigger_mock_breakout(symbol: str, price: float, resistance: float, emie: EnterpriseMarketIntelligenceEngine = Depends(get_emie)):
    detector = TechnicalEventDetector(emie)
    await detector.detect_breakout(symbol, price, resistance)
    return {"message": f"Breakout event injected for {symbol}"}

@router.post("/mock/corporate/results")
async def trigger_mock_results(symbol: str, revenue_growth: float, eps_growth: float, surprise_pct: float, emie: EnterpriseMarketIntelligenceEngine = Depends(get_emie)):
    detector = CorporateEventDetector(emie)
    await detector.inject_quarterly_results(symbol, revenue_growth, eps_growth, surprise_pct)
    return {"message": f"Results event injected for {symbol}"}
