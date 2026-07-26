import logging
from sqlalchemy.orm import Session
from event_engine.schemas import ScoredEvent
from decision_engine.database import AlertRecord

logger = logging.getLogger(__name__)

class SmartAlertsHandler:
    """
    Subscribes to Market Events and generates user-facing Alerts in the DB.
    Ensures duplicates are not generated (Module 8).
    """
    def __init__(self, db: Session):
        self.db = db
        
    async def handle_event(self, event: ScoredEvent):
        # We only alert users on HIGH/CRITICAL events or specific portfolio events
        if event.priority not in ["HIGH", "CRITICAL"] and event.type != "PORTFOLIO":
            return
            
        for symbol in event.symbols:
            # Check for duplicate alerts recently (e.g., in the last 24h)
            recent_alert = self.db.query(AlertRecord).filter(
                AlertRecord.symbol == symbol,
                AlertRecord.alert_type == event.subtype
            ).first() # Simplified check, real one checks timestamp > 24h ago
            
            if recent_alert:
                logger.debug(f"SmartAlerts suppressed duplicate alert for {symbol} - {event.subtype}")
                continue
                
            msg = f"{event.priority} Alert: {event.subtype} detected. Impact Score: {event.impact_score}"
            
            alert = AlertRecord(
                user_id="system_user", # Mock user
                portfolio_id=1,
                symbol=symbol,
                alert_type=event.subtype,
                message=msg,
                is_read=False
            )
            self.db.add(alert)
            self.db.commit()
            logger.info(f"Generated Smart Alert for {symbol}: {msg}")
