from portfolio_manager.database import SessionLocal
from portfolio_manager.portfolio_service import PortfolioService
from portfolio_manager.models import Portfolio, PortfolioSnapshot
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_daily_snapshots():
    """
    Called by APScheduler (e.g. 23:59 daily) to lock in the EOD snapshot of all portfolios.
    """
    db = SessionLocal()
    mds = MarketDataService(JugaadProvider())
    service = PortfolioService(db, mds)
    
    portfolios = db.query(Portfolio).all()
    for p in portfolios:
        try:
            summary = service.get_summary(p.id, p.user_id)
            snapshot = PortfolioSnapshot(
                portfolio_id=p.id,
                date=datetime.utcnow(),
                total_value=summary.total_portfolio_value,
                invested_value=summary.total_invested,
                cash_balance=summary.cash_balance,
                unrealized_pnl=summary.unrealized_pnl,
                realized_pnl=summary.realized_pnl,
                daily_return_pct=summary.today_pct or 0.0,
                risk_score=summary.risk_score,
                health_score=summary.health_score
            )
            db.add(snapshot)
        except Exception as e:
            logger.error(f"Failed to generate snapshot for portfolio {p.id}: {e}")
            
    db.commit()
    db.close()
    logger.info("Generated daily portfolio snapshots.")
