import logging
from market_data.models.dto import MarketQuote
from market_data.exceptions import DataValidationError

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates raw market data and raises exceptions or scores it."""

    @staticmethod
    def validate_quote(quote: MarketQuote) -> MarketQuote:
        if quote.close < 0 or quote.last_price < 0:
            raise DataValidationError(f"Negative price detected for {quote.symbol}: {quote.close}")
            
        if quote.high < quote.low:
            raise DataValidationError(f"High price ({quote.high}) is lower than Low price ({quote.low}) for {quote.symbol}")
            
        if quote.volume < 0:
            raise DataValidationError(f"Negative volume detected for {quote.symbol}")
            
        # Optional scoring deduction for missing non-critical fields
        score = 100
        if quote.vwap is None:
            score -= 10
        if quote.upper_circuit is None or quote.lower_circuit is None:
            score -= 10
            
        quote.validation_score = score
        return quote
