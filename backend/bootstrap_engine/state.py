from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import yaml

with open("config/bootstrap.yaml", "r") as f:
    config = yaml.safe_load(f)["bootstrap"]

engine = create_engine(f"sqlite:///{config['db_path']}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BootstrapRun(Base):
    __tablename__ = "bootstrap_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Pending") # Pending, Running, Completed, Failed
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, default=12)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

class SymbolTask(Base):
    __tablename__ = "symbol_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    step2_download = Column(String, default="Pending") # Pending, Success, Failed
    step3_validation = Column(String, default="Pending")
    step4_features = Column(String, default="Pending")
    step5_labels = Column(String, default="Pending")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
