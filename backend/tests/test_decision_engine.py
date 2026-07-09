import pytest
from unittest.mock import MagicMock
from decision_engine.regime.regime_classifier import RegimeClassifier
from decision_engine.scoring.scores import ScoringEngine
from decision_engine.orchestrator.adaptive_weight_engine import AdaptiveWeightEngine
from decision_engine.orchestrator.confidence_engine import ConfidenceEngine
from decision_engine.explainability.decision_explainer import DecisionExplainer
from data_platform.core.config_manager import ConfigManager

def test_regime_classifier():
    classifier = RegimeClassifier()
    assert classifier.classify(26.0, "UP") == "HighVolatility"
    assert classifier.classify(15.0, "UP") == "Bull"
    assert classifier.classify(15.0, "DOWN") == "Bear"

def test_scoring_engine():
    assert ScoringEngine.ml_score(0.75) == 75.0
    # wait, risk_score is 100 - (atr_pct * 10). 100 - (0.02 * 10) = 99.8
    assert ScoringEngine.risk_score(0.02) == 99.8

def test_adaptive_weight_engine():
    cm = ConfigManager()
    we = AdaptiveWeightEngine(cm)
    bull_weights = we.get_weights("Bull")
    bear_weights = we.get_weights("Bear")
    
    # Technical should be weighed more in Bull than Bear
    assert bull_weights.get("technical", 0) > bear_weights.get("technical", 0)

def test_confidence_engine():
    scores = {"technical": 85, "news": 85}
    conf = ConfidenceEngine.calculate_confidence(scores, model_agreement=0.9, data_freshness=1.0)
    # base = 90. No penalty. Boost = 10. Final = 100.
    assert conf == 100.0

def test_decision_explainer():
    explainer = DecisionExplainer()
    scores = {"technical": 85, "macro": 30}
    weights = {"technical": 0.35, "momentum": 0.25}
    explanation = explainer.explain("BEL", "BUY", 94.0, 75.0, "Bull", scores, weights)
    
    assert "BUY BEL (Confidence: 94.0%" in explanation
    assert "Technical (35.0%)" in explanation
    assert "Strong signals detected in: Technical" in explanation
    assert "Warning: Weakness remains in: Macro" in explanation
