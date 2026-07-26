from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from datetime import datetime
from .database import Base, engine

class ConversationLog(Base):
    """
    Stores AI-CIO conversation history for context (Module 13).
    """
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    portfolio_id = Column(Integer, index=True)
    
    role = Column(String) # user or assistant
    message = Column(Text)
    context_used_json = Column(JSON) # e.g., which agents contributed
    
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
