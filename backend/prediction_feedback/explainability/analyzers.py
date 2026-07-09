class SuccessAnalyzer:
    """Explains why a prediction succeeded."""
    
    @staticmethod
    def analyze(action: str, mfe: float, regime: str) -> str:
        factors = []
        if mfe > 10.0:
            factors.append("Strong Trend")
        if action == "BUY" and regime == "Bull":
            factors.append("Bull Market Tailwind")
        if not factors:
            factors.append("Normal Execution")
            
        return ", ".join(factors)

class FailureAnalyzer:
    """Explains why a prediction failed."""
    
    @staticmethod
    def analyze(action: str, mae: float, regime: str) -> str:
        factors = []
        if mae < -5.0:
            factors.append("Market Reversal")
        if action == "BUY" and regime == "Bear":
            factors.append("Bear Market Headwind")
        if not factors:
            factors.append("False Breakout / Whipsaw")
            
        return ", ".join(factors)
