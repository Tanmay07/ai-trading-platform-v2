from datetime import datetime
from typing import Optional
from market_data.providers.base_provider import MarketDataProvider
from market_data.models.dto import MarketStatus

class MarketStatusEngine:
    """Determines the true state of the market using provider data and time rules."""
    
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider
        
    def get_current_status(self) -> MarketStatus:
        # 1. Ask provider for the raw status
        raw_status = self.provider.get_market_status()
        
        # 2. Add local heuristics if provider is inaccurate or offline
        now = datetime.now()
        
        if raw_status.status == "Unknown":
            if now.weekday() >= 5:
                raw_status.status = "Weekend"
            elif 9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30):
                if now.hour == 9 and now.minute < 15:
                    raw_status.status = "Pre Open"
                else:
                    raw_status.status = "Open"
            else:
                raw_status.status = "Closed"
                
        return raw_status
