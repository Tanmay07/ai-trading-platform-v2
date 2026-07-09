from typing import Dict, Any

class TaskQueue:
    def __init__(self):
        # MVP: In-memory list acting as a queue
        self.queue = []
        
    def publish(self, topic: str, payload: Dict[str, Any]):
        """
        Publishes a message to a RabbitMQ/Redis queue.
        """
        message = {"topic": topic, "payload": payload}
        self.queue.append(message)
        print(f"[QUEUE] Published to {topic}: {payload}")
        
    def consume(self, topic: str) -> Optional[Dict[str, Any]]:
        for i, msg in enumerate(self.queue):
            if msg["topic"] == topic:
                return self.queue.pop(i)["payload"]
        return None
