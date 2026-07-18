import logging
import joblib
import pandas as pd
from pathlib import Path

from benchmarking.datasets.dataset_selector import DatasetSelector
from training_framework.optimization.training_runner import TrainingRunner
from production_training.deployment.production_registry import ProductionRegistry
from model_training.regression.lgbm_trade_quality_regressor import LGBMTradeQualityRegressor
from model_training.promotion.promotion_rules import PromotionRules

logger = logging.getLogger("ProductionTrainer")

class ProductionTrainer:
    def __init__(self):
        self.registry = ProductionRegistry()
        self.selector = DatasetSelector()
        
    def train_and_register(self, promote_immediately: bool = False):
        logger.info("Starting Production Training Pipeline (Classification & Regression)...")
        
        # Load Hybrid Mode (Champion from E3.7)
        df = self.selector.load_mode("hybrid")
        
        # Train Classifier (Primary)
        runner = TrainingRunner()
        exp_data = runner.run_training_cycle(df=df)
        
        lgb_trainer = runner.last_trainer
        if not lgb_trainer or not lgb_trainer.model:
            raise RuntimeError("TrainingRunner did not expose last_trainer model.")
            
        classifier_model = lgb_trainer.model
        
        # Train Regressor (Research)
        logger.info("Training Parallel Regression Model on Trade_Quality_Score...")
        if 'Date' in df.index.names:
            df_sorted = df.sort_index(level='Date')
        else:
            df_sorted = df.sort_index()
            
        # Ensure Trade_Quality_Score exists (mocking it if necessary)
        if 'Trade_Quality_Score' not in df_sorted.columns:
            # Synthetic quality for mock based on returns
            df_sorted['Trade_Quality_Score'] = (df_sorted.get('Target_Return_5d', 0) * 1000 + 50).clip(0, 100)
            
        dates = df_sorted.index.get_level_values('Date') if 'Date' in df_sorted.index.names else pd.Series(df_sorted.index)
        unique_dates = sorted(dates.unique())
        split_date_idx = int(len(unique_dates) * 0.8)
        split_date = unique_dates[split_date_idx]
        
        search_mask = dates <= split_date
        
        search_df = df_sorted[search_mask]
        
        # For regressor, early stopping needs train/val split of the search_df
        val_idx = int(len(search_df) * 0.9)
        train_df = search_df.iloc[:val_idx]
        val_df = search_df.iloc[val_idx:]
        
        drop_cols = ['Target_Breakout_Success', 'Target_Return_5d', 'symbol', 'Date', 'Trade_Quality_Score']
        features_used = [c for c in df_sorted.columns if c not in drop_cols]
        
        X_train_r = train_df[features_used]
        y_train_r = train_df['Trade_Quality_Score']
        X_val_r = val_df[features_used]
        y_val_r = val_df['Trade_Quality_Score']
        
        regressor = LGBMTradeQualityRegressor()
        regressor_model = regressor.train(X_train_r, y_train_r, X_val_r, y_val_r)
        
        # Evaluate regressor briefly on Val
        preds = regressor.predict(X_val_r)
        from sklearn.metrics import root_mean_squared_error, r2_score
        import numpy as np
        
        rmse = root_mean_squared_error(y_val_r, preds)
        r2 = r2_score(y_val_r, preds)
        
        logger.info(f"Regression Validation RMSE: {rmse:.2f}, R2: {r2:.2f}")
        
        # Prepare Metadata
        metadata = {
            "dataset_version": "v3",
            "feature_mode": "hybrid",
            "features": features_used,
            "metrics": exp_data.get("test_metrics", {}),
            "calibration": exp_data.get("calibration_method"),
            "optimal_threshold": exp_data.get("optimal_threshold"),
            "regression_metrics": {
                "rmse": float(rmse),
                "r2": float(r2)
            }
        }
        
        # Register in Registry
        version = self.registry.register_model(metadata)
        
        # Save models physically
        model_dir = Path(f"data/models/production/{version}")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(classifier_model, model_dir / "model.joblib") # Maintain backward compat
        joblib.dump(classifier_model, model_dir / "classifier.joblib")
        joblib.dump(regressor_model, model_dir / "regressor.joblib")
        
        # Save feature list
        import json
        with open(model_dir / "features.json", "w") as f:
            json.dump(features_used, f)
            
        if promote_immediately:
            active_model = self.registry.get_active_model()
            champ_metrics = active_model.get("metrics", {}) if active_model else {}
            
            rules = PromotionRules()
            promoted, reason = rules.evaluate(champ_metrics, metadata["metrics"])
            
            logger.info(f"Promotion Evaluation: {reason}")
            if promoted:
                self.registry.promote(version)
            
        logger.info(f"Production Model Bundle {version} successfully built and stored.")
        return version
