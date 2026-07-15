from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseBroker(ABC):
    """
    Abstract Base Class for all broker integrations (Zerodha, Upstox, Paper).
    Ensures that the OMS can interact with any broker using a standardized interface.
    """
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticates with the broker API and sets up the session."""
        pass
        
    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Returns account profile information."""
        pass
        
    @abstractmethod
    def get_margins(self) -> Dict[str, float]:
        """Returns available margin/funds. Expected format: {'available': float, 'utilized': float}"""
        pass
        
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Returns active positions."""
        pass
        
    @abstractmethod
    def place_order(self, symbol: str, quantity: int, side: str, order_type: str = "MARKET", price: float = 0.0) -> Dict[str, Any]:
        """
        Places an order.
        side: 'BUY' or 'SELL'
        order_type: 'MARKET', 'LIMIT', 'SL'
        Returns standard dict: {'order_id': str, 'status': str, 'message': str}
        """
        pass
        
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancels a pending order."""
        pass
