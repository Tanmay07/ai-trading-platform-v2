import logging
from typing import Dict, Any, Callable, List
from datetime import datetime

logger = logging.getLogger("EventBus")

class EventBus:
    """
    In-Memory Event Bus for the Trading Operations Engine.
    Provides Pub/Sub capabilities to decouple workflow stages.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        self.event_history.append(event)
        logger.info(f"Published Event: {event_type}")

        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber for {event_type}: {str(e)}")

# Global instance for the prototype
bus = EventBus()
