import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PortfolioContextEngine:
    """
    Analyzes the entire portfolio to provide context for individual recommendations.
    (e.g., if a stock is 30% of the portfolio, suggest Hold/Trim even if fundamental score is 90)
    """
    
    def analyze(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("Analyzing Portfolio Context")
        
        total_value = sum([h.get('market_value', 0) for h in holdings])
        if total_value == 0:
            return {"allocations": {}, "sectors": {}}
            
        allocations = {}
        sectors = {}
        
        for h in holdings:
            sym = h.get('symbol')
            mv = h.get('market_value', 0)
            sector = h.get('sector', 'N/A')
            weight = (mv / total_value) * 100
            
            allocations[sym] = round(weight, 2)
            sectors[sector] = sectors.get(sector, 0) + weight
            
        for k in sectors:
            sectors[k] = round(sectors[k], 2)
            
        return {
            "total_value": total_value,
            "allocations": allocations,
            "sectors": sectors
        }
