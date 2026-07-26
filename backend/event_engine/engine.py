import logging
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from .schemas import BaseEvent, ScoredEvent
from .models import MarketEventRecord, EventCorrelationRecord
from .bus import event_bus

logger = logging.getLogger(__name__)

class EnterpriseMarketIntelligenceEngine:
    """
    Module 1: The Brain of the Event Platform.
    Responsible for scoring, prioritizing, deduplicating, and correlating events.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def _calculate_impact_score(self, event: BaseEvent) -> float:
        """Module 4 - Event Scoring"""
        base_scores = {
            "CORPORATE": 80.0,
            "MARKET": 60.0,
            "TECHNICAL": 50.0,
            "MACRO": 90.0,
            "PORTFOLIO": 100.0
        }
        
        subtype_multipliers = {
            "QUARTERLY_RESULTS": 1.2,
            "GOLDEN_CROSS": 1.1,
            "RBI_POLICY": 1.5,
            "TARGET_ACHIEVED": 1.0,
            "STOP_LOSS_TRIGGERED": 1.0
        }
        
        score = base_scores.get(event.type, 50.0) * subtype_multipliers.get(event.subtype, 1.0)
        return min(100.0, round(score, 2))

    def _determine_priority(self, impact_score: float) -> str:
        """Module 5 - Event Prioritization"""
        if impact_score >= 90: return "CRITICAL"
        if impact_score >= 70: return "HIGH"
        if impact_score >= 50: return "MEDIUM"
        if impact_score >= 30: return "LOW"
        return "IGNORE"

    def _check_duplicate(self, event_id: str) -> bool:
        return self.db.query(MarketEventRecord).filter(MarketEventRecord.event_id == event_id).first() is not None

    async def process_raw_event(self, raw_event: BaseEvent):
        """
        Ingests a raw event from detectors, scores it, saves it to DB, and publishes 
        the scored event to the internal Event Bus for downstream modules.
        """
        if self._check_duplicate(raw_event.event_id):
            logger.info(f"Duplicate event suppressed: {raw_event.event_id}")
            return
            
        impact = self._calculate_impact_score(raw_event)
        priority = self._determine_priority(impact)
        
        if priority == "IGNORE":
            logger.debug(f"Event ignored due to low priority: {raw_event.event_id}")
            return
            
        scored_event = ScoredEvent(
            **raw_event.model_dump(),
            impact_score=impact,
            confidence=85.0, # Mock confidence for now
            priority=priority,
            expected_duration="MEDIUM_TERM",
            expected_direction="NEUTRAL"
        )
        
        # 1. Persist Event (Module 7 - Event Timeline)
        record = MarketEventRecord(
            event_id=scored_event.event_id,
            type=scored_event.type,
            subtype=scored_event.subtype,
            source=scored_event.source,
            symbols_json=scored_event.symbols,
            impact_score=scored_event.impact_score,
            confidence=scored_event.confidence,
            priority=scored_event.priority,
            expected_direction=scored_event.expected_direction,
            payload=scored_event.payload
        )
        self.db.add(record)
        self.db.commit()
        
        # 2. Correlate (Module 6)
        # Simplified correlation: find recent events for the same symbol
        if scored_event.symbols:
            recent_events = self.db.query(MarketEventRecord).filter(
                MarketEventRecord.type != scored_event.type,
                MarketEventRecord.event_id != scored_event.event_id
            ).order_by(MarketEventRecord.created_at.desc()).limit(3).all()
            
            # Simple mock logic: if we have recent events, correlate them
            if recent_events:
                corr_id = f"CORR_{uuid.uuid4().hex[:8]}"
                narrative = f"Multiple events affecting {', '.join(scored_event.symbols)} detected recently."
                corr_record = EventCorrelationRecord(
                    correlation_id=corr_id,
                    primary_event_id=scored_event.event_id,
                    related_event_ids_json=[r.event_id for r in recent_events],
                    narrative=narrative
                )
                self.db.add(corr_record)
                self.db.commit()
                logger.info(f"Generated correlation {corr_id}")
        
        # 3. Publish to Event Bus for downstream modules (Decision Engine, Alerts, etc.)
        await event_bus.publish(scored_event)
        logger.info(f"Scored & Published Event: {scored_event.event_id} ({scored_event.priority})")
