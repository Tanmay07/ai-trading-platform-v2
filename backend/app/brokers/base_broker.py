from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseBroker(ABC):
    @abstractmethod
    def login(self) -> bool: pass
    
    @abstractmethod
    def get_funds(self) -> float: pass
    
    @abstractmethod
    def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]: pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool: pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]: pass
