import json
import os
from datetime import datetime

class ModelRegistry:
    """
    Stores and manages model metadata, validation metrics, and champion/challenger statuses.
    """
    def __init__(self, registry_path: str = None):
        if registry_path is None:
            registry_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_registry.json')
        self.registry_path = registry_path
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"models": {}, "champion_id": None}
        
    def _save_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=4)
            
    def register_model(self, model_id: str, algo_name: str, metrics: dict, shap_importance: dict, hyperparams: dict, dataset_version: str):
        self.registry["models"][model_id] = {
            "model_id": model_id,
            "algorithm": algo_name,
            "training_date": datetime.now().isoformat(),
            "dataset_version": dataset_version,
            "hyperparameters": hyperparams,
            "metrics": metrics,
            "feature_importance": shap_importance,
            "status": "Research",
            "composite_score": self._compute_composite_score(metrics)
        }
        self._save_registry()
        
    def _compute_composite_score(self, metrics: dict) -> float:
        # Weighted Institutional Score
        # 40% Predictive Accuracy (ROC_AUC)
        # 40% Investment Performance (Sharpe_Ratio / 3 as a pseudo normalization)
        # 20% Robustness (1 - Max_Drawdown)
        
        auc = metrics.get('ROC_AUC', 0.5)
        sharpe = metrics.get('Sharpe_Ratio', 0.0)
        drawdown = metrics.get('Max_Drawdown', 1.0)
        
        # Normalize Sharpe loosely (assuming max around 3 for this timeframe)
        norm_sharpe = min(max(sharpe / 3.0, 0.0), 1.0)
        
        score = (auc * 0.4) + (norm_sharpe * 0.4) + ((1.0 - drawdown) * 0.2)
        return round(score * 100, 2)
        
    def promote_champion(self, model_id: str):
        if model_id not in self.registry["models"]:
            raise ValueError(f"Model {model_id} not found in registry.")
            
        old_champion = self.registry["champion_id"]
        if old_champion and old_champion in self.registry["models"]:
            self.registry["models"][old_champion]["status"] = "Challenger"
            
        self.registry["models"][model_id]["status"] = "Champion"
        self.registry["champion_id"] = model_id
        
        # Demote others to Research or Challenger based on score
        for m_id, meta in self.registry["models"].items():
            if m_id != model_id:
                if meta["composite_score"] > 60:
                    meta["status"] = "Challenger"
                else:
                    meta["status"] = "Research"
                    
        self._save_registry()
        
    def get_champion(self) -> dict:
        champ_id = self.registry["champion_id"]
        if champ_id:
            return self.registry["models"].get(champ_id)
        return None
        
    def get_all_models(self) -> dict:
        return self.registry["models"]
