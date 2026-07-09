from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

Base = declarative_base()

class SymbolMetadata(Base):
    __tablename__ = 'symbols_metadata'

    symbol = Column(String, primary_key=True)
    first_date = Column(DateTime, nullable=True)
    last_date = Column(DateTime, nullable=True)
    rows = Column(Integer, default=0)
    provider = Column(String, nullable=True)
    last_refresh = Column(DateTime, nullable=True)

class PostgresManager:
    """
    Manages connections and operations to the Metadata Database.
    Defaults to SQLite for local MVP unless Postgres URL is provided.
    """
    
    def __init__(self, db_url: str = "sqlite:///ai_trading_metadata.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Connected to metadata database at {db_url}")

    def update_metadata(self, symbol: str, first_date: datetime, last_date: datetime, rows: int, provider: str):
        """Updates the metadata for a downloaded symbol."""
        session = self.Session()
        try:
            record = session.query(SymbolMetadata).filter_by(symbol=symbol).first()
            if not record:
                record = SymbolMetadata(symbol=symbol)
                session.add(record)
                
            record.first_date = first_date
            record.last_date = last_date
            record.rows = rows
            record.provider = provider
            record.last_refresh = datetime.now()
            
            session.commit()
            logger.info(f"Updated metadata for {symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update metadata for {symbol}: {e}")
        finally:
            session.close()

    def get_metadata(self, symbol: str) -> dict:
        session = self.Session()
        try:
            record = session.query(SymbolMetadata).filter_by(symbol=symbol).first()
            if record:
                return {
                    "symbol": record.symbol,
                    "first_date": record.first_date,
                    "last_date": record.last_date,
                    "rows": record.rows,
                    "provider": record.provider,
                    "last_refresh": record.last_refresh
                }
            return {}
        finally:
            session.close()
