import os
import sys

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from portfolio_intelligence.engine import PortfolioIntelligenceEngine
from portfolio_intelligence.scenario_analyzer import ScenarioAnalyzer
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio

def run():
    print("Testing Portfolio Intelligence (Phase G7.5)...")
    
    engine = PortfolioIntelligenceEngine()
    workspace = engine.generate_daily_workspace()
    
    print("\n--- Portfolio Overview ---")
    port = workspace['portfolio']
    print(f"Total Value: ${port.get('total_value', 0):.2f}")
    print(f"Cash: ${port.get('cash_balance', 0):.2f}")
    
    print("\n--- Risk Analytics ---")
    risk = workspace['risk_analytics']
    print(f"Volatility: {risk['portfolio_volatility']*100:.2f}%")
    print(f"VaR (95%): ${risk['value_at_risk_95']:.2f}")
    print(f"Diversification Score: {risk['diversification_score']:.2f}")
    
    print("\n--- Recommendations (Optimized Sizing) ---")
    recs = workspace['recommendations']
    for r in recs:
        print(f"Symbol: {r['symbol']} | Rec: {r['recommendation']} | Conf: {r['confidence']:.2f}")
        print(f"  Suggested Investment: ${r['suggested_investment']:.2f}")
        print(f"  Target Weight: {r['target_weight']*100:.2f}%")
        
    print("\n--- Rebalancing Plan ---")
    plan = workspace['rebalancing_plan']
    print(f"Status: {plan['status']}")
    for act in plan['actions']:
        print(f"  Action: {act}")
        
    print("\n--- Scenario Analysis Simulation ---")
    if recs:
        test_sym = recs[0]['symbol']
        analyzer = ScenarioAnalyzer()
        try:
            positions = port.get('open_positions', [])
            impact = analyzer.simulate_trade(positions, port.get('cash_balance', 0.0), test_sym, 50000.0, 'BUY')
            print(f"Simulating BUY $50,000 of {test_sym}")
            print(f"  Volatility Delta: {impact['deltas']['volatility']*100:.4f}%")
            print(f"  VaR Delta: ${impact['deltas']['var_95']:.2f}")
        except Exception as e:
            print(f"Simulation failed: {e}")
            
    print("\nPhase G7.5 Verification Complete!")

if __name__ == "__main__":
    run()
