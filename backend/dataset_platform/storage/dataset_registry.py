from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml

with open("config/dataset_platform.yaml", "r") as f:
    config = yaml.safe_load(f)["dataset_platform"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, unique=True, index=True)
    dataset_type = Column(String) # classification, regression, ranking
    
    total_rows = Column(Integer, default=0)
    total_features = Column(Integer, default=0)
    
    quality_score = Column(Float, default=100.0)
    leakage_count = Column(Integer, default=0)
    
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    file_path = Column(String)
    file_hash = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

class DatasetRegistry:
    def __init__(self):
        init_db()
        
    def register_dataset(self, version_id: str, dataset_type: str, rows: int, features: int, quality: float, path: str, hash_val: str, start: datetime, end: datetime):
        db = SessionLocal()
        ds = DatasetVersion(
            version_id=version_id,
            dataset_type=dataset_type,
            total_rows=rows,
            total_features=features,
            quality_score=quality,
            file_path=path,
            file_hash=hash_val,
            start_date=start,
            end_date=end
        )
        db.add(ds)
        db.commit()
        db.close()
        
    def get_all(self):
        db = SessionLocal()
        res = db.query(DatasetVersion).order_by(DatasetVersion.created_at.desc()).all()
        db.close()
        return res
