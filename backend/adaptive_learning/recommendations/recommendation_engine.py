import pandas as pd
import numpy as np
import logging
from datetime import datetime
from model_training.registry.model_registry import ModelRegistry
from model_training.training.lightgbm_trainer import LightGBMTrainer
from model_training.training.xgboost_trainer import XGBoostTrainer
from model_training.training.catboost_trainer import CatBoostTrainer
from model_training.explainability.explainer import ModelExplainer
from adaptive_learning.db import AdaptiveLearningDB
import json

import os

logger = logging.getLogger("RecommendationEngine")

class RecommendationEngine:
    def __init__(self, dataset_path: str = None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dataset_v5.parquet')
        self.dataset_path = dataset_path
        self.registry = ModelRegistry()
        self.db = AdaptiveLearningDB()
        self.champion = self.registry.get_champion()
        self.model = self._load_champion_model()
        
    def generate_recommendations(self, performance: Dict[str, Any], drift_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates actionable recommendations based on analytics and drift.
        Does NOT automatically trigger retraining.
        """
        recs = []
        
        if performance.get("status") == "NO_DATA":
            return recs
            
        attr = performance.get("subsystem_attribution", {})
        
        if drift_report.get("prediction_drift"):
            recs.append({
                "priority": "HIGH",
                "owner": "Prediction Service",
                "recommendation": "Review recent model calibration or trigger Retraining Pipeline.",
                "evidence": f"Prediction attribution is negative ({attr.get('prediction')}) across recent sample.",
                "expected_impact": "Restore trade quality accuracy to baseline."
            })
            
        if attr.get("execution", 0) < 0:
            recs.append({
                "priority": "MEDIUM",
                "owner": "Execution Planning",
                "recommendation": "Adjust ATR multiplier to widen stop losses.",
                "evidence": f"Execution attribution is negative ({attr.get('execution')}). Stops may be too tight.",
                "expected_impact": "Reduce premature stop-outs in volatile regimes."
            })
            
        if not recs:
            recs.append({
                "priority": "LOW",
                "owner": "All Systems",
                "recommendation": "Maintain current configurations.",
                "evidence": "All subsystems are performing within expected baseline parameters.",
                "expected_impact": "Stable continued operation."
            })
            
        return recs

    def _load_champion_model(self):
        if not self.champion:
            raise ValueError("No champion model found in registry.")
            
        algo = self.champion["algorithm"]
        model_id = self.champion["model_id"]
        
        if algo == "LightGBM":
            trainer = LightGBMTrainer()
        elif algo == "XGBoost":
            trainer = XGBoostTrainer()
        elif algo == "CatBoost":
            trainer = CatBoostTrainer()
        else:
            raise ValueError(f"Unknown algorithm {algo}")
            
        trainer.load(model_id)
        return trainer

    def generate_daily_recommendations(self, top_k: int = 10) -> list:
        """
        Scans the universe, predicts, and returns the top K recommendations.
        Saves these to the Investment Journal.
        """
        logger.info(f"Generating recommendations using Champion Model: {self.champion['model_id']}")
        df = pd.read_parquet(self.dataset_path)
        if 'Date' in df.index.names:
            df = df.reset_index()
        
        # We need the most recent date for each symbol to simulate "today"
        latest_date = df['Date'].max()
        today_data = df[df['Date'] == latest_date].copy()
        
        exclude = ['Date', 'Symbol', 'Target_Forward_Return', 'Target_Class', 'Open', 'High', 'Low', 'Close', 'Volume']
        features = [c for c in today_data.columns if c not in exclude]
        
        X = today_data[features]
        symbols = today_data['Symbol'].values
        
        # Predict Proba
        probas = self.model.predict_proba(X)
        today_data['Confidence'] = probas
        
        # Get top K
        top_recs = today_data.sort_values(by='Confidence', ascending=False).head(top_k)
        
        explainer = ModelExplainer(self.model.model)
        
        recommendations = []
        for _, row in top_recs.iterrows():
            sym = row['Symbol']
            conf = row['Confidence']
            
            # Local SHAP for explainability
            x_instance = pd.DataFrame([row[features]])
            shap_dict = explainer.generate_global_importance(features, x_instance)
            top_factors = dict(list(shap_dict.items())[:3])
            
            rec = {
                "symbol": sym,
                "recommendation": "BUY" if conf > 0.5 else "HOLD",
                "confidence": float(conf),
                "expected_return": float(conf * 0.05), # Naive proxy for display
                "risk_score": float(1.0 - conf),
                "shap_explanation": top_factors,
                "date": str(latest_date)
            }
            recommendations.append(rec)
            
            # Write to Journal
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO investment_journal (date, symbol, recommendation, confidence, expected_return, shap_explanation, human_decision)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (str(latest_date), sym, rec["recommendation"], conf, rec["expected_return"], json.dumps(top_factors), "PENDING"))
                conn.commit()
                
        return recommendations
