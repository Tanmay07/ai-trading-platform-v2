import logging
from typing import Dict, List
from .risk_manager import RiskManager

logger = logging.getLogger("RebalancingAdvisor")

class RebalancingAdvisor:
    def __init__(self, max_asset_weight: float = 0.20, max_sector_weight: float = 0.40):
        self.max_asset_weight = max_asset_weight
        self.max_sector_weight = max_sector_weight
        self.risk_manager = RiskManager()
        
    def generate_plan(self, current_positions: List[Dict], total_value: float) -> Dict:
        """
        Generates a rebalancing plan if constraints are breached.
        """
        if total_value <= 0 or not current_positions:
            return {"status": "OK", "actions": []}
            
        actions = []
        sectors = {}
        
        # Check asset weights
        for pos in current_positions:
            val = pos['quantity'] * pos['entry_price']
            w = val / total_value
            
            sector = self.risk_manager._mock_sector(pos['symbol'])
            sectors[sector] = sectors.get(sector, 0) + w
            
            if w > self.max_asset_weight:
                overage = (w - self.max_asset_weight) * total_value
                actions.append({
                    "type": "REDUCE",
                    "symbol": pos['symbol'],
                    "reason": f"Position weight {w*100:.1f}% exceeds limit {self.max_asset_weight*100:.1f}%",
                    "suggested_amount": overage
                })
                
        # Check sector weights
        for sec, w in sectors.items():
            if w > self.max_sector_weight:
                overage_pct = w - self.max_sector_weight
                actions.append({
                    "type": "SECTOR_REDUCE",
                    "sector": sec,
                    "reason": f"Sector {sec} weight {w*100:.1f}% exceeds limit {self.max_sector_weight*100:.1f}%",
                    "suggested_reduction_pct": overage_pct
                })
                
        status = "REBALANCE_NEEDED" if actions else "OK"
        
        return {
            "status": status,
            "actions": actions
        }
