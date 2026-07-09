from app.ml.dataset_builder import DatasetBuilder
from app.ml.feature_selector import FeatureSelector
from app.ml.model_trainer import ModelTrainer
from app.ml.ensemble_engine import EnsembleEngine
from app.ml.meta_learner import MetaLearner
from app.ml.probability_calibrator import ProbabilityCalibrator
from app.ml.model_registry import ModelRegistry
from app.ml.experiment_tracker import ExperimentTracker
from app.ml.model_monitor import ModelMonitor
from sklearn.model_selection import train_test_split
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RetrainingEngine:
    def __init__(self):
        self.dataset_builder = DatasetBuilder()
        self.feature_selector = FeatureSelector()
        self.trainer = ModelTrainer()
        self.registry = ModelRegistry()
        self.tracker = ExperimentTracker()
        self.monitor = ModelMonitor()

    def run_pipeline(self) -> dict:
        """
        Orchestrates the entire ML retraining pipeline.
        """
        logger.info("Starting ML Retraining Pipeline...")
        
        # 1. Build Dataset
        X, y = self.dataset_builder.build_dataset()
        if X.empty or len(X) < 50:
            return {"status": "skipped", "reason": "Insufficient data"}
            
        # 2. Train-Test Split (Time-aware ideally, but for now simple split)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # 3. Feature Selection
        top_features = self.feature_selector.rank_features(X_train, y_train)
        X_train = X_train[top_features]
        X_test = X_test[top_features]
        
        # 4. Train Base Models
        xgb_model = self.trainer.train_xgboost(X_train, y_train)
        lgb_model = self.trainer.train_lightgbm(X_train, y_train)
        rf_model = self.trainer.train_random_forest(X_train, y_train)
        
        # 5. Setup Ensemble
        ensemble = EnsembleEngine({
            "xgboost": xgb_model,
            "lightgbm": lgb_model,
            "random_forest": rf_model
        })
        
        # 6. Train Meta Learner
        # We need out-of-fold predictions ideally, but for MVP we use train set
        train_probs = ensemble.predict_proba(X_train)
        meta_learner = MetaLearner()
        # Mocking meta features (AI consensus, regime) as they aren't fully integrated in historical yet
        X_meta_train = pd.DataFrame({'ensemble_prob': train_probs, 'consensus': 50, 'regime': 0})
        meta_learner.train(X_meta_train, y_train)
        
        # 7. Calibration
        calibrator = ProbabilityCalibrator()
        meta_train_probs = meta_learner.predict_proba(X_meta_train)
        calibrator.calibrate(meta_train_probs, y_train)
        
        # 8. Validation
        test_probs = ensemble.predict_proba(X_test)
        X_meta_test = pd.DataFrame({'ensemble_prob': test_probs, 'consensus': 50, 'regime': 0})
        meta_test_probs = meta_learner.predict_proba(X_meta_test)
        calibrated_test_probs = calibrator.predict(meta_test_probs)
        
        metrics = self.monitor.calculate_metrics(y_test, calibrated_test_probs)
        
        # 9. Register and Track
        model_pack = {
            "features": top_features,
            "xgb": xgb_model,
            "lgb": lgb_model,
            "rf": rf_model,
            "meta": meta_learner,
            "calibrator": calibrator
        }
        
        self.tracker.log_experiment("champion_ensemble", {}, metrics, top_features)
        
        if metrics.get("roc_auc", 0) > 0.5:  # Only save if better than random
            version = self.registry.save_model("champion_ensemble", model_pack, metrics)
            logger.info(f"Retraining successful. Promoted to {version}")
            return {"status": "success", "version": version, "metrics": metrics}
            
        return {"status": "failed", "reason": "Model performance below threshold"}

import pandas as pd
