import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class CompanyTagger:
    """Identifies NSE companies mentioned in text."""
    
    def __init__(self):
        # In production, this loads from data_platform.universe.symbol_master
        self.known_companies = {
            "RELIANCE": ["reliance", "ril"],
            "TCS": ["tcs", "tata consultancy"],
            "INFY": ["infy", "infosys"],
            "HDFCBANK": ["hdfc", "hdfc bank"],
            "BEL": ["bharat electronics", "bel"]
        }
        
    def tag_companies(self, text: str) -> List[str]:
        """Returns a list of NSE symbols found in the text."""
        text_lower = text.lower()
        
        found_symbols = []
        for symbol, aliases in self.known_companies.items():
            for alias in aliases:
                # Use regex word boundaries for accurate matching
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, text_lower):
                    found_symbols.append(symbol)
                    break # Don't add the same symbol twice if multiple aliases match
                    
        return found_symbols
