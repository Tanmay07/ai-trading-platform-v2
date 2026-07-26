import asyncio
import logging
from typing import Callable, Dict, List, Any
from .schemas import ScoredEvent

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-memory asynchronous Event Bus for routing Domain Events.
    For production, this would bridge to Kafka/Redis PubSub.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[ScoredEvent], Any]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._worker_task = None
        
    def subscribe(self, event_type: str, callback: Callable[[ScoredEvent], Any]):
        """Subscribe a callback to a specific event type (or '*' for all)."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed {callback.__name__} to event {event_type}")

    async def publish(self, event: ScoredEvent):
        """Publish an event to the bus."""
        await self._queue.put(event)
        logger.debug(f"Published event {event.event_id} of type {event.type}")

    async def _worker(self):
        """Background worker to process the event queue."""
        while self._running:
            try:
                event: ScoredEvent = await self._queue.get()
                
                # Find subscribers for this specific type, and catch-all '*'
                callbacks = self._subscribers.get(event.type, []) + self._subscribers.get('*', [])
                
                for cb in callbacks:
                    try:
                        # Fire and forget callback (could be async or sync)
                        if asyncio.iscoroutinefunction(cb):
                            asyncio.create_task(cb(event))
                        else:
                            # Run sync callbacks in threadpool to avoid blocking loop
                            asyncio.get_event_loop().run_in_executor(None, cb, event)
                    except Exception as e:
                        logger.error(f"Error in subscriber {cb.__name__} for event {event.event_id}: {e}")
                        
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event bus worker error: {e}")

    def start(self):
        """Start the background event processing."""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("Event Bus started.")

    async def stop(self):
        """Stop the background event processing."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            await asyncio.gather(self._worker_task, return_exceptions=True)
            logger.info("Event Bus stopped.")

# Global instance for the monolithic backend
event_bus = EventBus()
