from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml

with open("config/alpha_registry.yaml", "r") as f:
    config = yaml.safe_load(f)["alpha_registry"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AlphaFactor(Base):
    """
    Maintains the metadata and continuous evaluation state for every feature.
    """
    __tablename__ = "alpha_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    category = Column(String, index=True)
    formula = Column(String)
    
    version = Column(String, default="1.0")
    status = Column(String, default="Experimental") # Production, Experimental, Deprecated
    
    # Evaluation Metrics
    information_coefficient = Column(Float, default=0.0)
    rank_ic = Column(Float, default=0.0)
    quality_score = Column(Float, default=100.0)
    
    # Importance from ML runs
    shap_importance = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_evaluated = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
