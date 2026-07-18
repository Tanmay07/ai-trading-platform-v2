import os
import sys

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from adaptive_learning.recommendations.recommendation_engine import RecommendationEngine
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio
from paper_trading.monitoring.position_monitor import PositionMonitor
from adaptive_learning.drift.model_drift_detector import ModelDriftDetector

def run():
    print("Initializing Paper Trading Framework...")
    
    # 1. Daily Recommendations
    print("\n--- Generating Daily Recommendations (Champion Model) ---")
    engine = RecommendationEngine()
    recs = engine.generate_daily_recommendations(top_k=3)
    
    for r in recs:
        print(f"Symbol: {r['symbol']}, Rec: {r['recommendation']}, Confidence: {r['confidence']:.2f}")
        print(f"  Top Factors: {r['shap_explanation']}")
        
    # 2. Simulate a Human 'APPROVAL' of the top recommendation
    if recs:
        top_rec = recs[0]
        print(f"\n--- Simulating Human Approval for {top_rec['symbol']} ---")
        portfolio = VirtualPortfolio(initial_capital=1000000)
        
        # Assume entry at an arbitrary price, quantity 100
        portfolio.record_manual_entry(
            symbol=top_rec['symbol'],
            quantity=100,
            entry_price=105.50,
            ai_confidence=top_rec['confidence']
        )
        print("Trade recorded in Virtual Portfolio.")
        
    # 3. MTM
    print("\n--- Running Daily Portfolio MTM ---")
    monitor = PositionMonitor()
    monitor.run_daily_mtm()
    
    summary = portfolio.get_portfolio_summary()
    print(f"Portfolio Total Value: ${summary['total_value']:.2f}")
    print(f"Cash Balance: ${summary['cash_balance']:.2f}")
    
    # 4. Drift Check
    print("\n--- Checking Model Drift ---")
    drift = ModelDriftDetector()
    res = drift.check_drift()
    if res:
        print(f"Prediction Drift: {res['prediction_drift_score']}")
        print(f"Feature Drift: {res['feature_drift_score']}")
        print(f"Retraining Recommended: {res['retraining_recommended']}")
        
    print("\nPaper Trading Pipeline Execution Successful!")

if __name__ == "__main__":
    run()
