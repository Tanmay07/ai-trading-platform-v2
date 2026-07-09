import logging
from typing import Dict, Any

from decision_engine.regime.regime_classifier import RegimeClassifier
from decision_engine.scoring.scores import ScoringEngine
from decision_engine.orchestrator.adaptive_weight_engine import AdaptiveWeightEngine
from decision_engine.orchestrator.confidence_engine import ConfidenceEngine
from decision_engine.explainability.decision_explainer import DecisionExplainer
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class MetaDecisionEngine:
    """The central brain that aggregates, weights, and explains the final decision."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.regime_classifier = RegimeClassifier()
        self.weight_engine = AdaptiveWeightEngine(config_manager)
        self.confidence_engine = ConfidenceEngine()
        self.explainer = DecisionExplainer()
        
    def evaluate(self, symbol: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a stock and returns a comprehensive decision.
        `raw_inputs` contains raw ML probabilities, VIX, sentiment, etc.
        """
        logger.info(f"Evaluating Meta Decision for {symbol}")
        
        # 1. Determine Regime
        regime = self.regime_classifier.classify(
            raw_inputs.get("vix", 15.0), 
            raw_inputs.get("nifty_trend", "Neutral")
        )
        
        # 2. Get Adaptive Weights
        weights = self.weight_engine.get_weights(regime)
        
        # 3. Normalize Scores
        scores = {
            "technical": ScoringEngine.technical_score(
                raw_inputs.get("rsi", 50), raw_inputs.get("price", 100), raw_inputs.get("sma20", 90)
            ),
            "momentum": ScoringEngine.momentum_score(raw_inputs.get("relative_volume", 1.0)),
            "news": ScoringEngine.news_score(raw_inputs.get("sentiment_importance", 50)),
            "portfolio": ScoringEngine.portfolio_score(raw_inputs.get("portfolio_exposure", 0.05)),
            "macro": ScoringEngine.macro_score(raw_inputs.get("vix", 15.0)),
            "ml": ScoringEngine.ml_score(raw_inputs.get("ml_probability", 0.5)),
            "risk": ScoringEngine.risk_score(raw_inputs.get("atr_pct", 0.02))
        }
        
        # 4. Calculate Final Weighted Score (Expected Return proxy/ranking score)
        final_score = sum(scores.get(k, 0) * w for k, w in weights.items())
        
        # 5. Calculate Confidence
        confidence = self.confidence_engine.calculate_confidence(
            scores, 
            model_agreement=raw_inputs.get("model_agreement", 0.8),
            data_freshness=raw_inputs.get("data_freshness", 1.0)
        )
        
        # 6. Determine Action based on thresholds
        thresholds = self.config_manager.get_config("decision_engine").get("confidence", {})
        action = "HOLD"
        if confidence >= thresholds.get("threshold_buy", 80) and final_score > 60:
            action = "BUY"
        elif confidence >= thresholds.get("threshold_sell", 80) and final_score < 40:
            action = "SELL"
            
        # 7. Generate Explanation
        explanation = self.explainer.explain(symbol, action, confidence, final_score, regime, scores, weights)
        
        return {
            "symbol": symbol,
            "action": action,
            "confidence": round(confidence, 2),
            "final_score": round(final_score, 2),
            "regime": regime,
            "scores": scores,
            "explanation": explanation
        }
