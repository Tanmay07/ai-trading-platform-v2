import logging
from model_training.training.dataset_loader import DatasetLoader
from model_training.training.lightgbm_trainer import LightGBMTrainer
from model_training.validation.walkforward_validation import WalkforwardValidator
from model_training.explainability.feature_importance import extract_global_importance
from model_training.explainability.shap_analysis import SHAPAnalyzer
from model_training.registry.model_registry import ModelRegistry

logger = logging.getLogger("TrainingPipeline")

class TrainingPipeline:
    def __init__(self):
        self.loader = DatasetLoader()
        self.trainer = LightGBMTrainer()
        self.validator = WalkforwardValidator(self.trainer)
        self.registry = ModelRegistry()

    def run_training(self):
        """End-to-end model training pipeline."""
        logger.info("Starting production model training pipeline...")
        
        # 1. Load Data
        df = self.loader.load_dataset()
        if 'Target_Breakout_Success' not in df.columns:
            raise ValueError("Target_Breakout_Success not found in dataset!")
            
        # Optional: drop columns we don't want the model to train on (e.g., other targets, and strings)
        drop_cols = [c for c in df.columns if c.startswith('Target_') and c != 'Target_Breakout_Success']
        drop_cols.append('symbol')
        
        df = self.loader.perform_feature_selection(df, drop_cols=drop_cols)
        
        # 2. Time-series Split
        # Train: <= 2022, Val: 2023, Test: >= 2024
        train_set, val_set, test_set = self.loader.split_time_series(df, target_col='Target_Breakout_Success')
        X_train, y_train = train_set
        X_val, y_val = val_set
        X_test, y_test = test_set
        
        feature_names = X_train.columns.tolist()
        
        # 3. Train LightGBM
        model = self.trainer.train(X_train, y_train, X_val, y_val)
        
        # 4. Validate & Calibrate
        # Find forward return if available to pass to trading metrics
        returns_test = None # Not available unless we reconstruct it, but we can stick to hit rate for now
        ml_metrics, trade_metrics, calibrator = self.validator.evaluate(X_val, y_val, X_test, y_test, returns_test)
        
        # 5. Explainability (Feature Importance & SHAP)
        feat_imp_df = extract_global_importance(model, feature_names)
        
        shap_analyzer = SHAPAnalyzer(model)
        # Take a sample of the test set for SHAP summary to avoid memory issues
        sample_size = min(10000, len(X_test))
        X_test_sample = X_test.sample(n=sample_size, random_state=42)
        shap_values, base_value = shap_analyzer.generate_shap_values(X_test_sample)
        shap_summary_df = shap_analyzer.get_summary_stats(shap_values, feature_names)
        
        # 6. Metadata Compilation
        metadata = {
            "dataset": "dataset_v1.parquet",
            "hyperparameters": self.trainer.params,
            "metrics": {
                "ml": ml_metrics,
                "trading": trade_metrics
            },
            "feature_importance": feat_imp_df.head(20).to_dict(orient="records"),
            "shap_summary": shap_summary_df.to_dict(orient="records"),
            "base_value": float(base_value)
        }
        
        # 7. Register Model
        version = self.registry.register_model(model, calibrator, metadata, feature_names, is_production=True)
        
        logger.info(f"Pipeline completed successfully. Deployed Model Version: {version}")
        return version, metadata
