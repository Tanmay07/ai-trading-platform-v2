import asyncio
from app.recommendations.orchestrator import RecommendationEngine

def main():
    engine = RecommendationEngine()
    res = engine.generate_recommendations(portfolio_capital=100000, max_positions=2)
    print("\n--- E2E Result ---")
    print("Market Intelligence:")
    if 'market_intelligence' in res:
        for k, v in res['market_intelligence'].items():
            print(f"  {k}: {v}")
    
    print("\nRecommendations:")
    for r in res['recommendations']:
        print(f"  {r['Ticker']} | Score: {r.get('breakout_score')} | Conf: {r.get('Confidence')} | Qty: {r.get('Recommended_Quantity')}")
        
if __name__ == '__main__':
    main()
