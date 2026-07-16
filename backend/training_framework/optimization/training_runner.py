import logging
import time
import pandas as pd
from typing import Dict, Any

from model_training.training.dataset_loader import DatasetLoader
from model_training.training.lightgbm_trainer import LightGBMTrainer
from training_framework.optimization.randomized_search import RandomizedSearchOptimizer
from training_framework.evaluation.probability_calibration import CalibratorOptimizer
from training_framework.evaluation.threshold_optimizer import ThresholdOptimizer
from training_framework.registry.experiment_tracker import ExperimentTracker

logger = logging.getLogger("TrainingRunner")

class TrainingRunner:
    def __init__(self):
        self.loader = DatasetLoader()
        self.search_optimizer = RandomizedSearchOptimizer()
        self.calibrator_opt = CalibratorOptimizer()
        self.threshold_opt = ThresholdOptimizer()
        self.tracker = ExperimentTracker()
        
    def run_training_cycle(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Executes Phase 3 Nested Validation:
        1. Loads data and extracts train (2019-2023) and test (2024+).
        2. Runs RandomizedSearchCV on Train.
        3. Retrieves Best Parameters.
        4. Retrains LightGBM on full Train.
        5. Fits Calibrators on Train (or Val, but here Train for simplicity or OOB).
        6. Optimizes Threshold.
        7. Logs Experiment.
        """
        start_time = time.time()
        logger.info("Starting Institutional Training Cycle...")
        
        # 1. Load Data
        if df is None:
            df = self.loader.load_dataset()
            
            drop_cols = [c for c in df.columns if c.startswith('Target_') and c != 'Target_Breakout_Success']
            if 'symbol' in df.columns:
                drop_cols.append('symbol')
                
            df = self.loader.perform_feature_selection(df, drop_cols=drop_cols)
            
        if 'Target_Breakout_Success' not in df.columns:
            logger.warning("Target_Breakout_Success missing. Creating synthetic label from Target_Return_5d for testing.")
            df['Target_Breakout_Success'] = df['Target_Return_5d'] > 0.03
        
        # We MUST sort the dataframe chronologically for TimeSeriesSplit to work
        # Otherwise, if it is sorted by Symbol, the train/test splits will just split symbols instead of time.
        if 'Date' in df.index.names:
            df = df.sort_index(level='Date')
        else:
            df = df.sort_index()
            
        # Dynamically determine time-series split (80% Search/Train, 20% Final Test)
        dates = df.index.get_level_values('Date') if 'Date' in df.index.names else pd.Series(df.index)
        unique_dates = sorted(dates.unique())
        split_date_idx = int(len(unique_dates) * 0.8)
        
        if split_date_idx == 0:
             logger.error("Not enough dates to perform split.")
             raise ValueError("Insufficient data for train/test split.")
             
        split_date = unique_dates[split_date_idx]
        
        search_mask = dates <= split_date
        test_mask = dates > split_date
        
        search_df = df[search_mask]
        test_df = df[test_mask]
        
        X_search = search_df.drop(columns=['Target_Breakout_Success'])
        y_search = search_df['Target_Breakout_Success']
        
        X_test = test_df.drop(columns=['Target_Breakout_Success'])
        y_test = test_df['Target_Breakout_Success']
        
        logger.info(f"Search Set Size: {len(X_search)}, Test Set Size: {len(X_test)}")
        if len(X_search) < 100:
             logger.error("Search set is too small!")
             
        # We also need Trade Returns for the Test Set to evaluate
        trade_returns_test = test_df['Target_Return_5d'] if 'Target_Return_5d' in test_df.columns else pd.Series(0.0, index=test_df.index)
        
        # 2. Randomized Search
        search = self.search_optimizer.run_search(X_search, y_search)
        best_params = search.best_params_
        best_cv_score = search.best_score_
        
        # 3. Retrain on Full Search Set with Best Params
        logger.info("Retraining final model on complete Search Set with Best Parameters...")
        # Add early stopping params back in
        best_params['n_estimators'] = 500
        best_params['early_stopping_rounds'] = 50
        
        # For early stopping we need a holdout. We'll take the last 10% chronologically.
        split_idx = int(len(search_df) * 0.9)
        X_train_final, y_train_final = X_search.iloc[:split_idx], y_search.iloc[:split_idx]
        X_val_final, y_val_final = X_search.iloc[split_idx:], y_search.iloc[split_idx:]
        
        trainer = LightGBMTrainer(params=best_params)
        model = trainer.train(X_train_final, y_train_final, X_val_final, y_val_final)
        
        # 4. Calibration
        logger.info("Running Probability Calibration Optimization...")
        val_raw_prob = trainer.predict_proba(X_val_final)
        cal_results = self.calibrator_opt.fit_and_compare(val_raw_prob, y_val_final.values)
        
        # 5. Threshold Optimization
        logger.info("Running Threshold Optimization on Validation Set...")
        val_cal_prob = self.calibrator_opt.predict_proba(val_raw_prob)
        trade_returns_val = search_df['Target_Return_5d'].iloc[split_idx:] if 'Target_Return_5d' in search_df.columns else pd.Series(0.0, index=y_val_final.index)
        
        thresh_results = self.threshold_opt.optimize_threshold(val_cal_prob, y_val_final, trade_returns_val)
        
        # 6. Evaluate on Test Set
        logger.info("Evaluating Pipeline on Test Set...")
        test_raw_prob = trainer.predict_proba(X_test)
        test_cal_prob = self.calibrator_opt.predict_proba(test_raw_prob)
        
        test_trade_metrics = self.threshold_opt.optimize_threshold(test_cal_prob, y_test, trade_returns_test)
        # Find the metrics for the optimal threshold selected during validation
        opt_thresh = thresh_results["optimal_threshold"]
        test_metrics_at_opt = next((r for r in test_trade_metrics.get("all_results", []) if r["threshold"] == opt_thresh), {})
        
        end_time = time.time()
        duration_sec = end_time - start_time
        
        # 7. Log Experiment
        experiment_data = {
            "dataset_version": "dataset_v1.parquet",
            "model_version": "LightGBM_v2.0_CV",
            "validation_strategy": "Purged Walk-Forward Time-Series (5d Horizon, 7d Embargo)",
            "hyperparameters": best_params,
            "cv_score_roc_auc": float(best_cv_score),
            "calibration_method": cal_results["best_method"],
            "optimal_threshold": opt_thresh,
            "training_time_seconds": round(duration_sec, 2),
            "test_metrics": test_metrics_at_opt
        }
        
        exp_id = self.tracker.log_experiment(experiment_data)
        experiment_data["id"] = exp_id
        
        logger.info("Institutional Training Cycle Complete.")
        return experiment_data
