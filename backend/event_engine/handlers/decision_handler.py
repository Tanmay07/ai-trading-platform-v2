import logging
from event_engine.schemas import ScoredEvent
from policy_engine.engine import DecisionPolicyEngine
from policy_engine.models import PolicyVersion

logger = logging.getLogger(__name__)

class DecisionEventHandler:
    """
    Subscribes to Market Events. When a meaningful event occurs,
    automatically triggers the Decision Policy Engine to recalculate recommendations.
    """
    def __init__(self, engine: DecisionPolicyEngine, default_policy: PolicyVersion):
        self.engine = engine
        self.default_policy = default_policy
        
    async def handle_event(self, event: ScoredEvent):
        # We only care about events with HIGH or CRITICAL priority for immediate recalculation
        if event.priority not in ["HIGH", "CRITICAL"]:
            return
            
        logger.info(f"DecisionEventHandler reacting to {event.priority} event: {event.event_id}")
        
        for symbol in event.symbols:
            try:
                # In a real system, we'd lookup which portfolios hold this symbol 
                # and trigger a recalculation for each user.
                # For this mock, we assume portfolio_id 1 and a mock user
                
                # We mock current price as 1000.0 since we aren't querying the live MDS here
                current_price = 1000.0
                
                rec = self.engine.execute_policy(symbol, 1, "system_event_driven", current_price, self.default_policy)
                logger.info(f"Automatically recalculated recommendation for {symbol}: {rec.decision.value}")
                
            except Exception as e:
                logger.error(f"Error recalculating recommendation for {symbol}: {e}")
