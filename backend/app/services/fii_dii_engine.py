"""
FII / DII Engine
Tracks institutional money flow.
NOTE: Currently using simulated baseline data due to lack of free FII/DII API.
Ready for Phase 4 integration with a real data provider.
"""
from typing import Dict, Any
import random
from datetime import datetime

class FiiDiiEngine:
    def analyze(self) -> Dict[str, Any]:
        """
        Returns simulated institutional flow data.
        """
        # Baseline neutral values
        fii_net = random.choice([-500, 100, 500, 1500, -1500])
        dii_net = random.choice([-200, 400, 800, -800, 1200])
        
        fii_trend = "Buying" if fii_net > 0 else "Selling"
        dii_trend = "Buying" if dii_net > 0 else "Selling"
        
        score = 50
        if fii_net > 0 and dii_net > 0:
            score = 85
        elif fii_net > 0:
            score = 70
        elif dii_net > 0:
            score = 60
        else:
            score = 30
            
        return {
            "fii_score": score,
            "dii_score": score,  # using same for now
            "institutional_flow_score": score,
            "fii_trend": fii_trend,
            "dii_trend": dii_trend,
            "fii_net_flow": fii_net,
            "dii_net_flow": dii_net,
            "large_flow_events": abs(fii_net) > 1000
        }
