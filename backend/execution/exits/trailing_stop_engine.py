class TrailingStopEngine:
    def __init__(self, method: str = "atr"):
        self.method = method
        
    def generate_trailing_logic(self, atr: float) -> str:
        if self.method == "atr":
             return f"ATR x 2 ({atr * 2:.2f} trailing)"
        return "Fixed Percentage (5%)"
