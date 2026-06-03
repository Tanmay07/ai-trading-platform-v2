"""
Sector Strength Engine

Provides sector strength scoring. For MVP, maps stocks to predefined sectors
and assigns a base sector score.
"""
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

class SectorStrengthEngine:
    def __init__(self):
        self.logger = get_logger(__name__)
        # Mock sector strength for MVP
        self.sector_scores = {
            "Banking": 85,
            "IT": 60,
            "Pharma": 75,
            "FMCG": 55,
            "Auto": 80,
            "Capital Goods": 90,
            "Realty": 70,
            "Metals": 65,
            "Energy": 88
        }
        
        # Simple symbol to sector map
        self.symbol_to_sector = {
            "HDFCBANK.NS": "Banking", "ICICIBANK.NS": "Banking", "SBIN.NS": "Banking",
            "AXISBANK.NS": "Banking", "KOTAKBANK.NS": "Banking",
            "TCS.NS": "IT", "INFY.NS": "IT", "HCLTECH.NS": "IT", "WIPRO.NS": "IT", "LTIM.NS": "IT",
            "SUNPHARMA.NS": "Pharma",
            "ITC.NS": "FMCG", "HINDUNILVR.NS": "FMCG", "NESTLEIND.NS": "FMCG",
            "MARUTI.NS": "Auto", "TATAMOTORS.NS": "Auto", "M&M.NS": "Auto", "BAJAJ-AUTO.NS": "Auto",
            "LT.NS": "Capital Goods", "SIEMENS.NS": "Capital Goods",
            "DLF.NS": "Realty",
            "TATASTEEL.NS": "Metals", "JSWSTEEL.NS": "Metals",
            "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "NTPC.NS": "Energy", "POWERGRID.NS": "Energy"
        }

    def compute_sector_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Returns the sector strength score (0-100) for a given symbol.
        """
        sector = self.symbol_to_sector.get(symbol, "Unknown")
        
        if sector == "Unknown":
            return {
                "sector": "Unknown",
                "sector_score": 50.0,
                "reasons": ["Sector data unavailable"]
            }
            
        score = self.sector_scores.get(sector, 50)
        
        reasons = []
        if score > 80:
            reasons.append(f"{sector} sector is showing strong momentum")
        elif score < 40:
            reasons.append(f"{sector} sector is showing weakness")
            
        return {
            "sector": sector,
            "sector_score": float(score),
            "reasons": reasons
        }
