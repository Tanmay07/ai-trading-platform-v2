from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///decision_engine.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    user_id = Column(String, index=True)
    decision = Column(String)
    confidence = Column(Float)
    target_price_1 = Column(Float)
    target_price_2 = Column(Float)
    stop_loss = Column(Float)
    
    technical_score = Column(Float)
    valuation_score = Column(Float)
    portfolio_context_score = Column(Float)
    risk_score = Column(Float)
    
    explanation_why = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertRecord(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String, index=True)
    alert_type = Column(String) # e.g. "TARGET_REACHED", "STOP_LOSS_BREACHED"
    message = Column(Text)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class OpportunityRecord(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, unique=True)
    decision = Column(String)
    confidence = Column(Float)
    target_price_1 = Column(Float)
    expected_cagr = Column(Float)
    reason = Column(Text)
    scanned_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
