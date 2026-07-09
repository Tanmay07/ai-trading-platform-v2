class ScoringEngine:
    """Base class/namespace for various normalization scores (0-100)."""
    
    @staticmethod
    def technical_score(rsi: float, price: float, sma20: float) -> float:
        # Simple mock: Higher if RSI is healthy and price > SMA20
        score = 50.0
        if 40 < rsi < 70:
            score += 20
        if price > sma20:
            score += 30
        return min(100.0, score)
        
    @staticmethod
    def momentum_score(relative_volume: float) -> float:
        # Scale based on volume explosion
        score = min(100.0, relative_volume * 50)
        return score
        
    @staticmethod
    def news_score(sentiment_importance: int) -> float:
        # Directly uses Phase D4 importance score
        return float(sentiment_importance)
        
    @staticmethod
    def portfolio_score(current_exposure: float, max_exposure: float = 0.2) -> float:
        # Score drops if we already have too much exposure to this sector/stock
        ratio = current_exposure / max_exposure
        score = max(0.0, 100.0 * (1 - ratio))
        return score
        
    @staticmethod
    def macro_score(vix: float) -> float:
        # Score drops as VIX increases
        score = max(0.0, 100.0 - (vix * 2))
        return score
        
    @staticmethod
    def ml_score(probability: float) -> float:
        # Directly use calibrated ML probability 0-1 as 0-100
        return probability * 100.0
        
    @staticmethod
    def risk_score(atr_pct: float) -> float:
        # High ATR = High risk (score drops)
        score = max(0.0, 100.0 - (atr_pct * 10))
        return score
