"""
Strategies package for AI Trading Platform.

Provides rule-based trading strategies and a recommendation engine
that combines multiple signal sources to generate BUY/SELL/HOLD recommendations.

This is for educational and research purposes only, not financial advice.
"""

from app.strategies.rule_based_strategy import RuleBasedStrategy
from app.strategies.recommendation_engine import RecommendationEngine

__all__ = ["RuleBasedStrategy", "RecommendationEngine"]
