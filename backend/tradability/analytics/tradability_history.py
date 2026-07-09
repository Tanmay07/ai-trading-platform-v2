from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml

with open("config/tradability.yaml", "r") as f:
    config = yaml.safe_load(f)["tradability"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TradabilityScore(Base):
    """Stores the daily tradability score for every symbol."""
    __tablename__ = "tradability_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    total_score = Column(Float)
    category = Column(String) # Institutional Grade, Restricted, etc.
    
    # Component Scores (0-100)
    liquidity_score = Column(Float)
    volatility_score = Column(Float)
    execution_score = Column(Float)
    data_quality_score = Column(Float)
    circuit_score = Column(Float)

class PromotionEvent(Base):
    """Tracks when a stock changes categories (Promotions and Demotions)."""
    __tablename__ = "tradability_events"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    old_category = Column(String)
    new_category = Column(String)
    event_type = Column(String) # "PROMOTION" or "DEMOTION"
    reason = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
