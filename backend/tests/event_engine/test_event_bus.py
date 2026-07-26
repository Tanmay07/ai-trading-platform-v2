import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from event_engine.database import Base
from event_engine.engine import EnterpriseMarketIntelligenceEngine
from event_engine.schemas import BaseEvent, ScoredEvent
from event_engine.bus import EventBus
from datetime import datetime

# Setup test DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    bus.start()
    
    received_events = []
    
    def mock_subscriber(event: ScoredEvent):
        received_events.append(event)
        
    bus.subscribe("TECHNICAL", mock_subscriber)
    
    test_event = ScoredEvent(
        event_id="TEST_1",
        type="TECHNICAL",
        subtype="BREAKOUT",
        timestamp=datetime.utcnow(),
        source="Test",
        impact_score=80.0,
        confidence=90.0,
        priority="HIGH",
        expected_duration="SHORT_TERM",
        expected_direction="BULLISH"
    )
    
    await bus.publish(test_event)
    
    # Give the bus a moment to process the queue
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].event_id == "TEST_1"
    
    await bus.stop()

def test_engine_scoring_and_prioritization(db):
    emie = EnterpriseMarketIntelligenceEngine(db)
    
    raw = BaseEvent(
        event_id="TEST_2",
        type="MACRO",
        subtype="RBI_POLICY",
        timestamp=datetime.utcnow(),
        source="RBI",
        payload={}
    )
    
    score = emie._calculate_impact_score(raw)
    assert score == min(100.0, 90.0 * 1.5) # 100.0 (capped)
    
    priority = emie._determine_priority(score)
    assert priority == "CRITICAL"
