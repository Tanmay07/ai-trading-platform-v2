import os
import sys

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from executive_intelligence.cio_dashboard import CIODashboardEngine
from executive_intelligence.research_workspace import ResearchWorkspace

def run():
    print("Testing Executive Intelligence (Phase G7.6)...")
    
    engine = CIODashboardEngine()
    dash = engine.generate_dashboard()
    
    print("\n--- CIO Dashboard Assembly ---")
    print(f"Health Score: {dash['portfolio_health']['health_score']} (Grade {dash['portfolio_health']['grade']})")
    print(f"Alerts Generated: {len(dash['alerts'])}")
    
    print("\n--- Market Snapshot ---")
    market = dash['market_snapshot']
    print(market['summary_text'])
    
    print("\n--- Daily Investment Brief ---")
    print(dash['daily_brief'])
    
    print("\n--- Research Terminal API ---")
    ws = ResearchWorkspace()
    try:
        # Assuming we have a rec in the list
        if dash['recommendations']:
            sym = dash['recommendations'][0]['symbol']
            res = ws.get_stock_research(sym)
            print(f"Research for {sym}:")
            print(f"  AI Prediction: {res['ai_prediction']}")
            print(f"  Historical Accuracy: {res['historical_accuracy']*100:.1f}%")
            print(f"  Top Positive Driver: {res['explainability']['top_positive_factors'][0] if res['explainability']['top_positive_factors'] else 'N/A'}")
    except Exception as e:
        print(f"Failed to fetch research: {e}")
        
    print("\nPhase G7.6 Verification Complete!")

if __name__ == "__main__":
    run()
