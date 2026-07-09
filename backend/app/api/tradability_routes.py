from fastapi import APIRouter
from sqlalchemy import desc
from tradability.analytics.tradability_history import SessionLocal, TradabilityScore, PromotionEvent
from tradability.scoring.tradability_engine import TradabilityEngine

router = APIRouter(prefix="/api/tradability", tags=["Tradability Intelligence"])

@router.get("/")
def get_dashboard_summary():
    db = SessionLocal()
    # Mock data aggregation for UI
    stats = {
        "universe_size": 2348,
        "institutional_grade": 142,
        "highly_tradable": 310,
        "tradable": 512,
        "monitor": 204,
        "restricted": 1180,
        "avg_score": 52.4
    }
    db.close()
    return stats

@router.get("/promotions")
def get_recent_promotions():
    db = SessionLocal()
    events = db.query(PromotionEvent).order_by(desc(PromotionEvent.date)).limit(10).all()
    db.close()
    return [{"symbol": e.symbol, "type": e.event_type, "old": e.old_category, "new": e.new_category} for e in events]

@router.post("/recalculate")
def recalculate_universe():
    engine = TradabilityEngine()
    # Mock universe data
    dummy_data = {
        "RELIANCE": {"adtv_30": 500000000},
        "TCS": {"adtv_30": 300000000},
        "PENNYSTOCK": {"adtv_30": 1000}
    }
    results = engine.process_universe(dummy_data)
    return {"status": "success", "processed": len(results), "sample": results}
