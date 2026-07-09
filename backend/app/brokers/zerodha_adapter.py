from app.brokers.base_broker import BaseBroker
from typing import Dict, Any, List

class ZerodhaAdapter(BaseBroker):
    def login(self) -> bool: return True
    def get_funds(self) -> float: return 0.0
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]: return {}
    def cancel_order(self, order_id: str) -> bool: return True
    def get_positions(self) -> List[Dict[str, Any]]: return []
