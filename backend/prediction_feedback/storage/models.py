from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from prediction_feedback.storage.database import Base

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True)
    
    # State tracking
    state = Column(String(50), default="Generated") # Generated, Active, Completed, Evaluated, Archived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prediction details
    action = Column(String(20)) # BUY, SELL
    confidence = Column(Float)
    final_score = Column(Float)
    regime = Column(String(50))
    explanation = Column(Text)
    
    # Target / Stop Loss (populated when 'Active')
    entry_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    holding_period = Column(Integer, default=7)
    
    # Outcome tracking (populated when 'Evaluated')
    actual_return = Column(Float, nullable=True)
    mfe = Column(Float, nullable=True) # Max Favorable Excursion
    mae = Column(Float, nullable=True) # Max Adverse Excursion
    hit_target = Column(Boolean, nullable=True)
    hit_stoploss = Column(Boolean, nullable=True)
    expired = Column(Boolean, nullable=True)
    
    # Analyzed reasoning
    success_factors = Column(Text, nullable=True)
    failure_factors = Column(Text, nullable=True)
