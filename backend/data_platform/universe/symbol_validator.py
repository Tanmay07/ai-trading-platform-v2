import re

class SymbolValidator:
    """Validates equity symbols and ISINs."""
    
    @staticmethod
    def validate_nse_symbol(symbol: str) -> bool:
        """Validates if a string is a properly formatted NSE symbol."""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Strip '.NS' suffix if present for base validation
        base_symbol = symbol.replace('.NS', '').strip()
        
        if not base_symbol:
            return False
            
        # Basic rules: alphanumeric, hyphens, and ampersands, max 20 chars
        pattern = r'^[A-Z0-9\-&]{1,20}$'
        return bool(re.match(pattern, base_symbol.upper()))

    @staticmethod
    def validate_isin(isin: str) -> bool:
        """Validates if a string is a properly formatted ISIN."""
        if not isin or not isinstance(isin, str):
            return False
            
        # Basic format: 2 chars country code, 9 alphanumeric, 1 check digit
        pattern = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
        return bool(re.match(pattern, isin.upper()))
