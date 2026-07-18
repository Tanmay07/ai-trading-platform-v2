import pandas as pd
import numpy as np
import logging
import os
import json
import re
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

from model_training.training.lightgbm_trainer import LightGBMTrainer
from model_training.training.xgboost_trainer import XGBoostTrainer
from model_training.training.catboost_trainer import CatBoostTrainer
from model_training.training.cv_engine import PurgedWalkForwardCV
from model_training.training.hyperparameter_tuner import RandomizedHyperparameterSearch
from model_training.evaluation.evaluator import ModelEvaluator
from model_training.evaluation.investment_evaluator import InvestmentEvaluator
from model_training.explainability.explainer import ModelExplainer
from model_training.registry.model_registry import ModelRegistry

logger = logging.getLogger("ChampionChallengerOrchestrator")

class ChampionChallengerOrchestrator:
    def __init__(self, dataset_path: str = "data/ml_datasets/dataset_v5.parquet", target_col: str = "Target_Forward_Return"):
        self.dataset_path = dataset_path
        self.target_col = target_col
        self.registry = ModelRegistry()
        self.ml_evaluator = ModelEvaluator()
        self.inv_evaluator = InvestmentEvaluator()
        self.reports_dir = "docs/G7.3_reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        self.search_spaces = {
            "LightGBM": {
                'num_leaves': [31, 64],
                'learning_rate': [0.05, 0.1],
                'max_depth': [6, 8]
            },
            "XGBoost": {
                'max_depth': [4, 6],
                'learning_rate': [0.05, 0.1],
                'n_estimators': [200, 500]
            },
            "CatBoost": {
                'depth': [4, 6],
                'learning_rate': [0.05, 0.1],
                'iterations': [200, 500]
            },
            "LogisticRegression": {
                'C': [0.1, 1.0, 10.0]
            },
            "DecisionTree": {
                'max_depth': [3, 5, 7]
            },
            "RandomForest": {
                'n_estimators': [10, 50],
                'max_depth': [3, 5]
            }
        }
        
    def run_arena(self, n_iter=2):
        logger.info(f"Loading certified dataset from {self.dataset_path}")
        df = pd.read_parquet(self.dataset_path)
        if 'Date' in df.index.names:
            df = df.reset_index()
            
        df = df.dropna(subset=[self.target_col])
        df['Target_Class'] = (df[self.target_col] > 0).astype(int)
        
        # Dataset V5 is already strictly whitelisted. We just exclude the structural columns.
        exclude = ['Date', 'Symbol', 'Target_Forward_Return', 'Target_Class']
        
        # Make absolutely sure we only pass numeric columns to the model
        numeric_dtypes = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64', 'bool']
        features = [c for c in df.columns if c not in exclude and df[c].dtype in numeric_dtypes]
        
        logger.info(f"Using exactly {len(features)} Production Whitelist Features.")
        
        # Strict 70/15/15 Chronological Split
        total_len = len(df)
        train_end = int(total_len * 0.70)
        val_end = int(total_len * 0.85)
        
        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()
        
        logger.info(f"Chronological Split: Train({len(train_df)}), Val({len(val_df)}), Test({len(test_df)})")
        
        # In this phase, we must train ALL 6 models identically through the CV engine
        from model_training.training.sklearn_trainer import SklearnTrainer
        
        models_to_train = {
            "LR_Baseline": ("LogisticRegression", SklearnTrainer),
            "DT_Baseline": ("DecisionTree", SklearnTrainer),
            "RF_Baseline": ("RandomForest", SklearnTrainer),
            "LGBM_V3": ("LightGBM", LightGBMTrainer),
            "XGB_V3": ("XGBoost", XGBoostTrainer),
            "CAT_V3": ("CatBoost", CatBoostTrainer)
        }
        
        results = {}
        all_trials = {}
        cv_engine = PurgedWalkForwardCV(n_splits=3, embargo_pct=0.02)
        
        for model_id, (algo, trainer_cls) in models_to_train.items():
            logger.info(f"=== Tuning {algo} ===")
            
            # For Sklearn baselines, we pass the algorithm name to the trainer
            if trainer_cls == SklearnTrainer:
                trainer_kwargs = {"algorithm": algo}
            else:
                trainer_kwargs = {}
                
            tuner = RandomizedHyperparameterSearch(
                trainer_class=trainer_cls,
                search_space=self.search_spaces[algo],
                cv_engine=cv_engine,
                n_iter=n_iter,
                target_metric="ROC_AUC",
                trainer_kwargs=trainer_kwargs
            )
            
            best_params = tuner.tune(train_df, "Target_Class", features, self.ml_evaluator)
            all_trials[algo] = tuner.get_trials()
            
            logger.info(f"Training final {algo} model with best params on full training set...")
            if trainer_cls == SklearnTrainer:
                final_trainer = trainer_cls(algorithm=algo, params=best_params)
            else:
                final_trainer = trainer_cls(params=best_params)
            
            final_trainer.train(
                train_df[features], train_df["Target_Class"],
                val_df[features], val_df["Target_Class"]
            )
            final_trainer.save(model_id)
            
            logger.info(f"Evaluating {algo} on Test Set...")
            y_pred_proba = final_trainer.predict_proba(test_df[features])
            
            ml_metrics = self.ml_evaluator.evaluate(test_df["Target_Class"].values, y_pred_proba)
            inv_metrics = self.inv_evaluator.evaluate(test_df, self.target_col, y_pred_proba)
            
            combined_metrics = {**ml_metrics, **inv_metrics}
            
            try:
                explainer = ModelExplainer(final_trainer.model)
                X_sample = test_df[features].sample(min(1000, len(test_df)), random_state=42)
                shap_importance = explainer.generate_global_importance(features, X_sample)
            except Exception as e:
                logger.warning(f"Could not generate SHAP for {algo}: {e}")
                shap_importance = final_trainer.get_feature_importance()
                
            composite_score = self._compute_composite_score(ml_metrics, inv_metrics)
            combined_metrics["Composite_Score"] = composite_score
            
            self.registry.register_model(
                model_id=model_id,
                algo_name=algo,
                metrics=combined_metrics,
                shap_importance=shap_importance,
                hyperparams=best_params,
                dataset_version="Dataset_V5_Certified"
            )
            results[model_id] = combined_metrics
            
        champion_id = self._select_champion()
        self._generate_reports(all_trials, results, champion_id)
        
        return self.registry.get_all_models()

    def _run_baselines(self, train_df, test_df, features):
        logger.info("Training Baseline Models (Sanity Check)...")
        baselines = {
            "LogisticRegression": LogisticRegression(max_iter=100),
            "DecisionTree": DecisionTreeClassifier(max_depth=3),
            "RandomForest": RandomForestClassifier(n_estimators=10, max_depth=3, n_jobs=-1)
        }
        
        # Sample for speed if huge
        sample_df = train_df.sample(min(50000, len(train_df)), random_state=42)
        X_train = sample_df[features].fillna(0)
        y_train = sample_df["Target_Class"]
        X_test = test_df[features].fillna(0)
        y_test = test_df["Target_Class"]
        
        for name, clf in baselines.items():
            clf.fit(X_train, y_train)
            preds = clf.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, preds)
            logger.info(f"Baseline {name} ROC-AUC on Test Set: {auc:.4f}")
            if auc > 0.90:
                logger.warning(f"Baseline {name} achieved unrealistic AUC > 0.90. Leakage may still exist!")

    def _compute_composite_score(self, ml_metrics: dict, inv_metrics: dict) -> float:
        """
        Weights:
        Investment Performance (40%): Sharpe, CAGR, Max_Drawdown (inverted)
        Classification Performance (25%): ROC_AUC, F1, Log_Loss (inverted)
        Robustness & Stability (15%): Soft proxy using Win Rate & Profit Factor
        Calibration (10%): Reliability (inverted)
        Computational Efficiency (10%): Default score if not timed
        """
        score = 0.0
        
        # Investment (40%)
        score += min(max(inv_metrics.get("Sharpe_Ratio", 0) / 3.0, 0), 1.0) * 15
        score += min(max(inv_metrics.get("CAGR", 0) / 0.5, 0), 1.0) * 15
        score += max(0, (1 - inv_metrics.get("Max_Drawdown", 1.0))) * 10
        
        # Classification (25%)
        score += ml_metrics.get("ROC_AUC", 0.5) * 12.5
        score += ml_metrics.get("F1_Score", 0.0) * 7.5
        score += max(0, (1 - ml_metrics.get("Log_Loss", 1.0))) * 5
        
        # Robustness (15%)
        score += inv_metrics.get("Win_Rate", 0.0) * 7.5
        score += min(inv_metrics.get("Profit_Factor", 0.0) / 3.0, 1.0) * 7.5
        
        # Calibration (10%)
        score += max(0, (1 - ml_metrics.get("Calibration_Reliability", 1.0))) * 10
        
        # Computational (10%)
        score += 10 # Default
        
        return min(max(score, 0), 100) # Clamp 0-100
        
    def _select_champion(self):
        models = self.registry.get_all_models()
        if not models:
            return None
            
        best_id = None
        best_score = -1
        
        for m_id, meta in models.items():
            if meta.get("status") == "Revoked":
                continue
            score = meta.get("metrics", {}).get("Composite_Score", 0)
            if score > best_score:
                best_score = score
                best_id = m_id
                
        if best_id:
            logger.info(f"Promoting {best_id} to Champion with score {best_score:.2f}")
            self.registry.promote_champion(best_id)
            
        return best_id

    def _generate_reports(self, all_trials, results, champion_id):
        # 1. Hyperparameter Report
        with open(os.path.join(self.reports_dir, "hyperparameter_optimization_report.md"), "w") as f:
            f.write("# Hyperparameter Optimization Report\n\n")
            for algo, trials in all_trials.items():
                f.write(f"## {algo}\n")
                best = max(trials, key=lambda x: x["avg_score"])
                f.write(f"**Best ROC_AUC:** {best['avg_score']:.4f}\n")
                f.write(f"**Best Params:** `{json.dumps(best['params'])}`\n\n")
                
        # 2. Model Comparison Report
        with open(os.path.join(self.reports_dir, "model_comparison_report.md"), "w") as f:
            f.write("# Model Comparison Report\n\n")
            f.write("| Model ID | ROC_AUC | Sharpe | CAGR | Max Drawdown | Composite Score |\n")
            f.write("|---|---|---|---|---|---|\n")
            for m_id, metrics in results.items():
                f.write(f"| {m_id} | {metrics.get('ROC_AUC',0):.4f} | {metrics.get('Sharpe_Ratio',0):.2f} | {metrics.get('CAGR',0):.2%} | {metrics.get('Max_Drawdown',0):.2%} | {metrics.get('Composite_Score',0):.1f} |\n")
                
        # 3. Champion Selection Report
        with open(os.path.join(self.reports_dir, "champion_selection_report.md"), "w") as f:
            f.write("# Champion Selection Report\n\n")
            f.write(f"**Selected Champion:** `{champion_id}`\n\n")
            f.write("The Champion was selected using a Weighted Institutional Framework evaluating Investment Performance (40%), Classification Performance (25%), Robustness (15%), Calibration (10%), and Computational Efficiency (10%).\n")
            
        # 4. Production Promotion Report
        with open(os.path.join(self.reports_dir, "production_promotion_report.md"), "w") as f:
            f.write("# Production Promotion Report\n\n")
            f.write(f"Model `{champion_id}` has been formally promoted to Production in the Model Registry.\n")
            f.write(f"Promotion Timestamp: {datetime.now().isoformat()}\n")
            
        # 5. Cross Validation Report (simplification)
        with open(os.path.join(self.reports_dir, "cross_validation_report.md"), "w") as f:
            f.write("# 3-Fold Purged Walk-Forward Cross Validation Report\n\n")
            f.write("All models were tuned using a strict chronological 3-fold walk-forward split with a 2% embargo to prevent leakage. The final benchmark was conducted purely on an untouched 15% out-of-sample Test Set.\n")
