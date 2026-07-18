from typing import List, Dict, Any

class FeatureGenerator:
    """
    Simulates the generation of experimental features for the Alpha Lab MVP.
    """
    def generate_candidate_factors(self) -> List[Dict[str, str]]:
        # 5 Mock Experimental Factors
        return [
            {
                "name": "MACD Divergence Momentum",
                "source": "Technical",
                "author": "Quant_Team_A",
                "logic": "Calculates divergence between MACD histogram and price over 14 days."
            },
            {
                "name": "Volatility Expansion Breakout",
                "source": "Technical",
                "author": "Quant_Team_B",
                "logic": "Flags when daily ATR expands by > 1.5x the 20-day average."
            },
            {
                "name": "Sector Relative Strength",
                "source": "Market Structure",
                "author": "Quant_Team_A",
                "logic": "Stock performance divided by Sector ETF performance over 30 days."
            },
            {
                "name": "Institutional Block Deal Imbalance",
                "source": "Alternative",
                "author": "Data_Team_X",
                "logic": "Net block deal volume vs average daily volume."
            },
            {
                "name": "Earnings Surprise Momentum",
                "source": "Fundamental",
                "author": "Quant_Team_C",
                "logic": "Post-earnings drift factor based on unexpected EPS beat."
            }
        ]
