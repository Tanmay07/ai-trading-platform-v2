class MarketDataError(Exception):
    """Base class for all market data exceptions."""
    pass

class ProviderTimeoutError(MarketDataError):
    """Raised when the data provider does not respond in time."""
    pass

class ProviderRateLimitError(MarketDataError):
    """Raised when the data provider rate limit is exceeded."""
    pass

class InvalidSymbolError(MarketDataError):
    """Raised when the requested symbol is invalid or not found."""
    pass

class StaleDataError(MarketDataError):
    """Raised when the provider returns data that is too old."""
    pass

class DataValidationError(MarketDataError):
    """Raised when data fails strict validation checks (e.g., negative prices)."""
    pass

class ProviderUnavailableError(MarketDataError):
    """Raised when the provider is completely unreachable."""
    pass
