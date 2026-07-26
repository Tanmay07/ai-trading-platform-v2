from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base, engine

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    investment_style = Column(String) # e.g., Growth, Value, Momentum
    benchmark = Column(String, default="NIFTY50")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan", foreign_keys="[PolicyVersion.policy_id]")
    
    # Optional shortcut to active version
    active_version_id = Column(Integer, ForeignKey('policy_versions.id', use_alter=True), nullable=True)

class PolicyVersion(Base):
    __tablename__ = "policy_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    version_number = Column(Integer)
    
    status = Column(String, default="DRAFT") # DRAFT, ACTIVE, ARCHIVED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Complex Configurations stored as JSON for flexibility
    weights = Column(JSON)      # Tech, Val, Context, Risk weights
    thresholds = Column(JSON)   # Score mapped to DecisionCategory
    target_logic = Column(JSON) # e.g., {"methodology": "ATR_PROJECTION", "multiplier": 1.5}
    stop_loss_logic = Column(JSON) 
    sizing_rules = Column(JSON) 
    review_rules = Column(JSON)
    market_regime_rules = Column(JSON)
    
    policy = relationship("Policy", back_populates="versions", foreign_keys=[policy_id])

class DecisionAuditLog(Base):
    """
    Every decision must be fully auditable and reproducible.
    """
    __tablename__ = "decision_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    policy_version_id = Column(Integer, ForeignKey("policy_versions.id"))
    
    # Inputs snapshot
    market_data_snapshot = Column(JSON)
    portfolio_context_snapshot = Column(JSON)
    
    # Computation details
    scores_breakdown = Column(JSON)
    
    # Outputs
    decision = Column(String)
    confidence = Column(Float)
    target_price_1 = Column(Float)
    stop_loss = Column(Float)
    explanation = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
