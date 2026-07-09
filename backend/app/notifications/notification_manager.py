from typing import Dict, Any

class NotificationManager:
    def notify(self, message: str):
        """
        Dispatches message to configured channels.
        """
        print(f"[NOTIFICATION] {message}")
