import logging
import yaml
from typing import Dict, Any

from research.registry.alpha_registry import AlphaRegistry
from research.alpha_lab.feature_generator import FeatureGenerator
from research.statistical.ic_analyzer import ICAnalyzer
from research.trading.alpha_backtester import AlphaBacktester
from research.stability.regime_analysis import RegimeAnalysis
from research.ranking.alpha_ranker import AlphaRanker

logger = logging.getLogger("SignalDiscovery")

class SignalDiscoveryEngine:
    """
    Orchestrates the evaluation of a candidate alpha signal through all R&D pipelines.
    """
    def __init__(self):
        self.registry = AlphaRegistry()
        self.feature_gen = FeatureGenerator()
        self.ic_analyzer = ICAnalyzer()
        self.backtester = AlphaBacktester()
        self.regime_analyzer = RegimeAnalysis()
        self.ranker = AlphaRanker()
        
        with open("config/alpha_research.yaml", "r") as f:
            self.config = yaml.safe_load(f)["alpha_research"]

    def run_discovery_pipeline(self):
        """
        Runs the full discovery loop on the 5 MVP features.
        """
        logger.info("Starting Signal Discovery Pipeline")
        features = self.feature_gen.generate_candidate_factors()
        
        for feat in features:
            # 1. Register in Marketplace as Experimental
            signal = self.registry.register_signal(feat["name"], feat["source"], feat["author"])
            signal_id = signal["signal_id"]
            logger.info(f"Evaluating {feat['name']}...")
            
            # 2. Run Evaluations
            stat_metrics = self.ic_analyzer.evaluate(feat["name"])
            trade_metrics = self.backtester.evaluate(feat["name"])
            stab_metrics = self.regime_analyzer.evaluate(feat["name"])
            
            # 3. Rank
            alpha_score = self.ranker.generate_score(stat_metrics, trade_metrics, stab_metrics)
            
            # 4. Promotion Recommendation Check
            recommended = "REJECTED"
            if alpha_score >= self.config["minimum_alpha_score"]:
                if stat_metrics["ic"] >= self.config["minimum_ic"]:
                    if trade_metrics["precision_at_20"] >= self.config["minimum_precision_at_20"]:
                        recommended = "RECOMMENDED_FOR_CANDIDATE"
                        
            evaluation_record = {
                "statistical": stat_metrics,
                "trading": trade_metrics,
                "stability": stab_metrics,
                "alpha_score": alpha_score,
                "promotion_recommendation": recommended
            }
            
            self.registry.update_evaluation(signal_id, evaluation_record)
            
            if recommended == "RECOMMENDED_FOR_CANDIDATE":
                self.registry.promote_signal(signal_id, "Candidate")
                
        logger.info("Signal Discovery Pipeline Complete.")
