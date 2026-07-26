import uuid
from datetime import datetime
from event_engine.schemas import BaseEvent
from event_engine.engine import EnterpriseMarketIntelligenceEngine

class CorporateEventDetector:
    """
    Monitors Exchange filings and Corporate Actions.
    """
    def __init__(self, emie: EnterpriseMarketIntelligenceEngine):
        self.emie = emie
        
    async def inject_quarterly_results(self, symbol: str, revenue_growth: float, eps_growth: float, surprise_pct: float):
        event = BaseEvent(
            event_id=f"CORP_{uuid.uuid4().hex[:8]}",
            type="CORPORATE",
            subtype="QUARTERLY_RESULTS",
            timestamp=datetime.utcnow(),
            source="BSE/NSE Filing",
            symbols=[symbol],
            sectors=[],
            portfolios=[],
            payload={
                "revenue_growth": revenue_growth,
                "eps_growth": eps_growth,
                "surprise_pct": surprise_pct
            }
        )
        await self.emie.process_raw_event(event)

    async def inject_dividend_announcement(self, symbol: str, dividend_yield: float):
        event = BaseEvent(
            event_id=f"CORP_{uuid.uuid4().hex[:8]}",
            type="CORPORATE",
            subtype="DIVIDEND_ANNOUNCEMENT",
            timestamp=datetime.utcnow(),
            source="Board Meeting Output",
            symbols=[symbol],
            sectors=[],
            portfolios=[],
            payload={"dividend_yield": dividend_yield}
        )
        await self.emie.process_raw_event(event)
