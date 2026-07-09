from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from market_intelligence.storage.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    hash_id = Column(String(64), unique=True, index=True, nullable=False)
    source = Column(String(50), index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    published_time = Column(DateTime, default=datetime.utcnow, index=True)
    
    # NLP Outputs
    sentiment_label = Column(String(20), nullable=True) # Positive, Neutral, Negative
    sentiment_score = Column(Float, nullable=True)
    sentiment_confidence = Column(Float, nullable=True)
    
    importance_score = Column(Integer, nullable=True) # 0-100
    
    company_tags = Column(String(500), nullable=True) # Comma separated for now
    event_classification = Column(String(100), nullable=True)
    
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketMemoryEvent(Base):
    __tablename__ = "market_memory_events"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True)
    event_type = Column(String(100), index=True)
    event_date = Column(DateTime, index=True)
    
    # Outcomes
    t_plus_1_return = Column(Float, nullable=True)
    t_plus_3_return = Column(Float, nullable=True)
    t_plus_7_return = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
