from typing import Dict, Any, List
from app.ml.feature_store import FeatureStore
from app.ml.prediction_engine import PredictionEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MLOrchestrator:
    def __init__(self):
        self.feature_store = FeatureStore()
        self.prediction_engine = PredictionEngine()
        
    async def process_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw features, logs them to Feature Store, and runs Inference.
        Returns ML predictions to be injected into the candidate.
        """
        ticker = candidate_data.get("Ticker", "UNKNOWN")
        
        # 1. Snapshot for auto-retraining later (asynchronous logic or fast insert)
        # Note: in real prod, target_hit is calculated days later. Here we just store features.
        try:
            self.feature_store.store_snapshot(ticker, candidate_data)
        except Exception as e:
            logger.error(f"Feature Store Error: {e}")
            
        # 2. ML Inference
        try:
            predictions = self.prediction_engine.predict(candidate_data)
        except Exception as e:
            logger.error(f"Prediction Error: {e}")
            predictions = {"buy_probability": 0.5, "model_version": "error"}
            
        return predictions
