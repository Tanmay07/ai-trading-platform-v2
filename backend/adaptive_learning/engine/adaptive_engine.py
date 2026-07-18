import yaml
import logging
from typing import Dict, Any

from adaptive_learning.analytics.trade_analyzer import TradeAnalyzer
from adaptive_learning.drift.drift_detector import DriftDetector
from adaptive_learning.recommendations.recommendation_engine import RecommendationEngine
from adaptive_learning.reporting.ai_cio_synthesizer import AICIOSynthesizer

logger = logging.getLogger("AdaptiveEngine")

class AdaptiveEngine:
    def __init__(self):
        with open("config/adaptive_learning.yaml", "r") as f:
            self.config = yaml.safe_load(f)["adaptive_learning"]
            
        self.analyzer = TradeAnalyzer()
        self.drift_detector = DriftDetector()
        self.recommendation_engine = RecommendationEngine()
        self.ai_cio = AICIOSynthesizer()
        
    def analyze_system_health(self) -> Dict[str, Any]:
        """
        Orchestrates the Adaptive Intelligence pipeline.
        1. Analyzes trade feedback repository.
        2. Detects drift.
        3. Generates recommendations.
        4. Synthesizes the AI-CIO executive briefing.
        """
        logger.info("Starting Adaptive Intelligence diagnostics...")
        
        # 1. Performance Analytics
        performance = self.analyzer.analyze_performance()
        
        # 2. Drift Detection
        drift_report = self.drift_detector.detect_drift(performance, self.config["thresholds"])
        
        # 3. Recommendations
        recommendations = self.recommendation_engine.generate_recommendations(performance, drift_report)
        
        # 4. AI-CIO Briefing
        briefing = self.ai_cio.generate_briefing(performance, drift_report, recommendations)
        
        # Compile System Health Payload
        health_score = int(performance.get("win_rate", 0) * 100) if performance.get("status") != "NO_DATA" else 0
        
        return {
            "health_score": health_score,
            "performance": performance,
            "drift_report": drift_report,
            "recommendations": recommendations,
            "ai_cio_briefing": briefing
        }
