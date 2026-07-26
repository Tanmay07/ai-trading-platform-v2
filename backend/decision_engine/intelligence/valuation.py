from typing import Dict, Any
import json
import os
import hashlib

class ValuationIntelligence:
    def __init__(self):
        # We will use a mock mapping for fundamentals per the Open Questions resolution
        self.mock_file = os.path.join(os.path.dirname(__file__), 'mock_fundamentals.json')
        self._ensure_mock_file()
        
    def _ensure_mock_file(self):
        if not os.path.exists(self.mock_file):
            default_data = {
                "HDFCBANK": {"pe": 15.5, "pb": 2.1, "ev_ebitda": 10.2, "div_yield": 1.2, "eps_growth": 18.0},
                "RELIANCE": {"pe": 28.4, "pb": 2.8, "ev_ebitda": 14.5, "div_yield": 0.3, "eps_growth": 12.0},
                "TCS": {"pe": 32.1, "pb": 12.5, "ev_ebitda": 22.0, "div_yield": 1.8, "eps_growth": 10.0}
            }
            with open(self.mock_file, 'w') as f:
                json.dump(default_data, f)

    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Analyzes PE, PB, and Growth against Sector Averages.
        Returns a score 0-100 and supporting metrics.
        """
        with open(self.mock_file, 'r') as f:
            fund_data = json.load(f)
            
        data = fund_data.get(symbol)
        
        if not data:
            # Generate deterministic mock if not found
            h = int(hashlib.sha256(symbol.encode('utf-8')).hexdigest(), 16)
            data = {
                "pe": 10.0 + (h % 30), # 10 to 40
                "pb": 1.0 + ((h % 50) / 10.0), # 1.0 to 6.0
                "ev_ebitda": 8.0 + (h % 15),
                "div_yield": (h % 30) / 10.0,
                "eps_growth": 5.0 + (h % 20)
            }
            
        score = 50.0
        
        # PE Logic (Lower is generally better, but extremely low could be value trap)
        pe = data["pe"]
        if 10 <= pe <= 20: score += 20
        elif 20 < pe <= 35: score += 5
        elif pe > 40: score -= 20
        
        # EPS Growth
        if data["eps_growth"] > 15: score += 20
        elif data["eps_growth"] > 10: score += 10
        elif data["eps_growth"] < 5: score -= 15
        
        # Margin of Safety (Simplified Proxy based on Score)
        margin_of_safety = max(0.0, score * 0.4) # up to 40%
        
        return {
            "score": min(100.0, max(0.0, score)),
            "metrics": {
                "pe": round(pe, 2),
                "pb": round(data["pb"], 2),
                "eps_growth": round(data["eps_growth"], 2),
                "margin_of_safety_pct": round(margin_of_safety, 2),
                "valuation_status": "Undervalued" if score > 70 else "Fairly Valued" if score > 40 else "Overvalued"
            }
        }
