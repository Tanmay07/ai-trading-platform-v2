import logging
from sqlalchemy import desc
from tradability.analytics.tradability_history import SessionLocal, TradabilityScore
from tradability.monitoring import promotion_engine, demotion_engine

logger = logging.getLogger("TradabilityMonitor")

class TradabilityMonitor:
    
    TIER_RANK = {
        "Institutional Grade": 5,
        "Highly Tradable": 4,
        "Tradable": 3,
        "Monitor": 2,
        "Restricted": 1
    }

    @classmethod
    def compare_daily_shifts(cls, symbol: str):
        """
        Looks at the last 2 scores for a symbol. If the category changed, it fires
        promotion_engine or demotion_engine.
        """
        db = SessionLocal()
        scores = db.query(TradabilityScore).filter(TradabilityScore.symbol == symbol).order_by(desc(TradabilityScore.date)).limit(2).all()
        db.close()
        
        if len(scores) < 2:
            return # Not enough history
            
        today = scores[0].category
        yesterday = scores[1].category
        
        if today == yesterday:
            return
            
        today_rank = cls.TIER_RANK.get(today, 0)
        yesterday_rank = cls.TIER_RANK.get(yesterday, 0)
        
        if today_rank > yesterday_rank:
            logger.info(f"[{symbol}] PROMOTED: {yesterday} -> {today}")
            promotion_engine.handle_promotion(symbol, yesterday, today)
        elif today_rank < yesterday_rank:
            logger.warning(f"[{symbol}] DEMOTED: {yesterday} -> {today}")
            demotion_engine.handle_demotion(symbol, yesterday, today)
