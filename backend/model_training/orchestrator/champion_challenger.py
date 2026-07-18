import pandas as pd
import logging
from feature_platform.validation.validation_pipeline import ValidationPipeline
from model_training.training.lightgbm_trainer import LightGBMTrainer
from model_training.training.xgboost_trainer import XGBoostTrainer
from model_training.training.catboost_trainer import CatBoostTrainer
from model_training.evaluation.evaluator import ModelEvaluator
from model_training.explainability.explainer import ModelExplainer
from model_training.registry.model_registry import ModelRegistry
from sklearn.model_selection import train_test_split

logger = logging.getLogger("ChampionChallengerOrchestrator")

class ChampionChallengerOrchestrator:
    def __init__(self, dataset_path: str = "data/dataset_v5.parquet", target_col: str = "Target_Forward_Return"):
        self.dataset_path = dataset_path
        self.target_col = target_col
        self.registry = ModelRegistry()
        self.evaluator = ModelEvaluator()
        
    def run_arena(self, test_size=0.2):
        logger.info(f"Loading dataset from {self.dataset_path}")
        df = pd.read_parquet(self.dataset_path)
        if 'Date' in df.index.names:
            df = df.reset_index()
        
        # We need to create a binary target for classification if it's continuous
        # e.g., > 0 is 1 (Positive return)
        if self.target_col not in df.columns:
             df[self.target_col] = df.groupby('Symbol')['Close'].pct_change(5).shift(-5)
             
        df = df.dropna(subset=[self.target_col])
        df['Target_Class'] = (df[self.target_col] > 0).astype(int)
        
        exclude = ['Date', 'Symbol', 'Target_Forward_Return', 'Target_Class', 'Open', 'High', 'Low', 'Close', 'Volume']
        features = [c for c in df.columns if c not in exclude]
        
        X = df[features]
        y = df['Target_Class']
        
        # Chronological Split (No shuffle to prevent time leakage)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, shuffle=False)
        
        models_to_train = {
            "LGBM_V1": ("LightGBM", LightGBMTrainer()),
            "XGB_V1": ("XGBoost", XGBoostTrainer()),
            "CAT_V1": ("CatBoost", CatBoostTrainer())
        }
        
        results = {}
        
        for model_id, (algo, trainer) in models_to_train.items():
            logger.info(f"Training {algo}...")
            trainer.train(X_train, y_train, X_val, y_val)
            trainer.save(model_id)
            
            logger.info(f"Evaluating {algo}...")
            y_pred_proba = trainer.predict_proba(X_val)
            metrics = self.evaluator.evaluate(y_val.values, y_pred_proba)
            
            logger.info(f"Generating SHAP for {algo}...")
            explainer = ModelExplainer(trainer.model)
            # Use small sample for global SHAP calculation efficiency
            X_sample = X_val.sample(min(1000, len(X_val)), random_state=42)
            shap_importance = explainer.generate_global_importance(features, X_sample)
            
            # If SHAP failed, fallback to native feature importance
            if not shap_importance:
                shap_importance = trainer.get_feature_importance()
                
            self.registry.register_model(
                model_id=model_id,
                algo_name=algo,
                metrics=metrics,
                shap_importance=shap_importance,
                hyperparams=trainer.params,
                dataset_version="Dataset_V5"
            )
            results[model_id] = metrics
            
        # Champion Selection
        self._select_champion()
        return self.registry.get_all_models()
        
    def _select_champion(self):
        models = self.registry.get_all_models()
        if not models:
            return
            
        best_id = None
        best_score = -1
        
        for m_id, meta in models.items():
            score = meta.get("composite_score", 0)
            if score > best_score:
                best_score = score
                best_id = m_id
                
        if best_id:
            logger.info(f"Promoting {best_id} to Champion with score {best_score}")
            self.registry.promote_champion(best_id)
