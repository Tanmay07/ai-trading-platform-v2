from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml

with open("config/scenario_dataset.yaml", "r") as f:
    config = yaml.safe_load(f)["scenario_datasets"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScenarioDataset(Base):
    __tablename__ = "scenario_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, unique=True, index=True)
    parent_version_id = Column(String, index=True)
    
    scenario_category = Column(String) # Regime, Sector, Volatility, Event
    scenario_name = Column(String)     # Bull, IT, High VIX, Budget
    
    total_rows = Column(Integer, default=0)
    total_symbols = Column(Integer, default=0)
    
    quality_score = Column(Float, default=100.0)
    
    file_path = Column(String)
    file_hash = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

class ScenarioRegistry:
    def __init__(self):
        init_db()
        
    def register_scenario(self, version_id: str, parent_id: str, category: str, name: str, rows: int, symbols: int, quality: float, path: str, hash_val: str):
        db = SessionLocal()
        ds = ScenarioDataset(
            version_id=version_id,
            parent_version_id=parent_id,
            scenario_category=category,
            scenario_name=name,
            total_rows=rows,
            total_symbols=symbols,
            quality_score=quality,
            file_path=path,
            file_hash=hash_val
        )
        db.add(ds)
        db.commit()
        db.close()
        
    def get_all(self):
        db = SessionLocal()
        res = db.query(ScenarioDataset).order_by(ScenarioDataset.created_at.desc()).all()
        db.close()
        return res
