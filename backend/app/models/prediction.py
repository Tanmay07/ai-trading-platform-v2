"""
Prediction ORM Models

Defines Prediction and PredictionOutcome tables.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Prediction(Base):
    """Stores an AI-generated prediction / recommendation for a symbol."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    predicted_direction = Column(String(10), nullable=True)     # UP / DOWN / NEUTRAL
    predicted_probability = Column(Float, nullable=True)
    recommended_action = Column(String(10), nullable=True)      # BUY / SELL / HOLD
    confidence_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    entry_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    time_horizon = Column(String(20), nullable=True)            # e.g. "1d", "1w"
    model_version = Column(String(50), nullable=True)
    reasons = Column(JSON, nullable=True)

    # Relationship to outcomes
    outcomes = relationship("PredictionOutcome", back_populates="prediction")

    def __repr__(self) -> str:
        return (
            f"<Prediction(symbol={self.symbol!r}, "
            f"action={self.recommended_action!r}, "
            f"confidence={self.confidence_score})>"
        )


class PredictionOutcome(Base):
    """Tracks the actual outcome of a prediction for accuracy measurement."""

    __tablename__ = "prediction_outcomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    actual_1d_return = Column(Float, nullable=True)
    actual_3d_return = Column(Float, nullable=True)
    actual_5d_return = Column(Float, nullable=True)
    was_correct = Column(Integer, nullable=True)  # 1=correct, 0=incorrect
    evaluated_at = Column(DateTime, server_default=func.now())

    prediction = relationship("Prediction", back_populates="outcomes")

    def __repr__(self) -> str:
        return f"<PredictionOutcome(prediction_id={self.prediction_id}, correct={self.was_correct})>"
