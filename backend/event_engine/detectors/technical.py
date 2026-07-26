import uuid
from datetime import datetime
from event_engine.schemas import BaseEvent
from event_engine.engine import EnterpriseMarketIntelligenceEngine

class TechnicalEventDetector:
    """
    Monitors market data for technical signals.
    In a real system, this runs continuously over a websocket or polling loop.
    For Phase P4, we provide a trigger mechanism to inject mocked events.
    """
    def __init__(self, emie: EnterpriseMarketIntelligenceEngine):
        self.emie = emie
        
    async def detect_breakout(self, symbol: str, current_price: float, resistance: float):
        """Simulates detecting a price breakout."""
        if current_price > resistance:
            event = BaseEvent(
                event_id=f"TECH_{uuid.uuid4().hex[:8]}",
                type="TECHNICAL",
                subtype="BREAKOUT",
                timestamp=datetime.utcnow(),
                source="TechnicalAnalyzer",
                symbols=[symbol],
                sectors=[],
                portfolios=[],
                payload={"price": current_price, "resistance_broken": resistance}
            )
            await self.emie.process_raw_event(event)

    async def detect_golden_cross(self, symbol: str):
        event = BaseEvent(
            event_id=f"TECH_{uuid.uuid4().hex[:8]}",
            type="TECHNICAL",
            subtype="GOLDEN_CROSS",
            timestamp=datetime.utcnow(),
            source="TechnicalAnalyzer",
            symbols=[symbol],
            sectors=[],
            portfolios=[],
            payload={"message": "50 DMA crossed above 200 DMA"}
        )
        await self.emie.process_raw_event(event)
