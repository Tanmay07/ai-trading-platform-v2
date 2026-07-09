from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml
import logging

logger = logging.getLogger("CheckpointManager")

with open("config/bootstrap.yaml", "r") as f:
    config = yaml.safe_load(f)["bootstrap"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BootstrapCheckpoint(Base):
    __tablename__ = "bootstrap_checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, index=True)
    stage_name = Column(String, index=True)
    
    status = Column(String) # Pending, Running, Completed, Failed, Skipped
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    
    # Store partial progress if the stage supports it (e.g., 500/2000 symbols done)
    progress_current = Column(Integer, default=0)
    progress_total = Column(Integer, default=0)
    
    error_message = Column(String, nullable=True)
    
def init_db():
    Base.metadata.create_all(bind=engine)

class CheckpointManager:
    def __init__(self):
        init_db()
        
    def start_stage(self, execution_id: str, stage_name: str, total_items: int = 0):
        db = SessionLocal()
        existing = db.query(BootstrapCheckpoint).filter_by(execution_id=execution_id, stage_name=stage_name).first()
        
        if existing:
            existing.status = "Running"
            existing.start_time = datetime.utcnow()
            existing.progress_total = total_items
        else:
            cp = BootstrapCheckpoint(
                execution_id=execution_id,
                stage_name=stage_name,
                status="Running",
                start_time=datetime.utcnow(),
                progress_total=total_items
            )
            db.add(cp)
            
        db.commit()
        db.close()
        
    def complete_stage(self, execution_id: str, stage_name: str, status: str = "Completed", error: str = None):
        db = SessionLocal()
        cp = db.query(BootstrapCheckpoint).filter_by(execution_id=execution_id, stage_name=stage_name).first()
        if cp:
            cp.status = status
            cp.end_time = datetime.utcnow()
            if status == "Completed":
                cp.progress_current = cp.progress_total
            if error:
                cp.error_message = error
            db.commit()
        db.close()
        
    def get_execution_state(self, execution_id: str) -> dict:
        db = SessionLocal()
        checkpoints = db.query(BootstrapCheckpoint).filter_by(execution_id=execution_id).all()
        db.close()
        
        return {
            cp.stage_name: {
                "status": cp.status,
                "progress": f"{cp.progress_current}/{cp.progress_total}" if cp.progress_total > 0 else "N/A",
                "error": cp.error_message
            } for cp in checkpoints
        }
