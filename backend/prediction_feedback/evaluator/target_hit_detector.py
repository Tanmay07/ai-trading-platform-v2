class TargetHitDetector:
    """Detects if a target was hit during the holding period."""
    
    @staticmethod
    def check_target(action: str, target_price: float, high_price: float, low_price: float) -> bool:
        if not target_price:
            return False
            
        if action == "BUY":
            return high_price >= target_price
        elif action == "SELL":
            return low_price <= target_price
        return False
