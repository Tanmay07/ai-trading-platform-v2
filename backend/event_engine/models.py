from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from datetime import datetime
from .database import Base, engine

class MarketEventRecord(Base):
    """
    Event Timeline Storage (Module 7).
    """
    __tablename__ = "market_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    type = Column(String, index=True) # CORPORATE, MARKET, TECHNICAL, MACRO
    subtype = Column(String, index=True)
    source = Column(String)
    
    symbols_json = Column(JSON) # List of affected symbols
    
    impact_score = Column(Float)
    confidence = Column(Float)
    priority = Column(String) # CRITICAL, HIGH, MEDIUM, LOW, IGNORE
    expected_direction = Column(String)
    
    payload = Column(JSON)
    resolution_status = Column(String, default="OPEN") # OPEN, RESOLVED, ARCHIVED
    
    created_at = Column(DateTime, default=datetime.utcnow)

class EventCorrelationRecord(Base):
    """
    Module 6 - Event Correlation.
    """
    __tablename__ = "event_correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, unique=True)
    primary_event_id = Column(String, index=True)
    related_event_ids_json = Column(JSON)
    narrative = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)
