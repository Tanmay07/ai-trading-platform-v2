import os
import sys

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from model_training.orchestrator.champion_challenger import ChampionChallengerOrchestrator
from model_training.registry.model_registry import ModelRegistry

def run():
    print("Initializing Model Arena...")
    
    # Path relative to backend root where script should be run from
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_v5.parquet')
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run G7.2 validate_features.py first.")
        return
        
    orchestrator = ChampionChallengerOrchestrator(dataset_path=data_path)
    
    print("Starting Model Training and Benchmarking...")
    orchestrator.run_arena()
    
    registry = ModelRegistry()
    champion = registry.get_champion()
    
    print("\n--- Model Arena Results ---")
    all_models = registry.get_all_models()
    for m_id, meta in all_models.items():
        print(f"\nModel: {m_id} ({meta['algorithm']})")
        print(f"Status: {meta['status']}")
        print(f"Composite Score: {meta['composite_score']}")
        print(f"ROC-AUC: {meta['metrics'].get('ROC_AUC', 0):.4f}")
        print(f"Sharpe Ratio: {meta['metrics'].get('Sharpe_Ratio', 0):.4f}")
        
    print("\n---------------------------")
    if champion:
        print(f"🏆 CHAMPION MODEL: {champion['model_id']} ({champion['algorithm']}) 🏆")
        print(f"Score: {champion['composite_score']}")
    else:
        print("No champion selected.")

if __name__ == "__main__":
    run()
