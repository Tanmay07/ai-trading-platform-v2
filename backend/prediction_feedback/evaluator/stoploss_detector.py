class StoplossDetector:
    """Detects if a stop loss was hit during the holding period."""
    
    @staticmethod
    def check_stoploss(action: str, stop_loss: float, high_price: float, low_price: float) -> bool:
        if not stop_loss:
            return False
            
        if action == "BUY":
            return low_price <= stop_loss
        elif action == "SELL":
            return high_price >= stop_loss
        return False
