def calculate(symbol_data: dict) -> float:
    """
    Calculates Liquidity Score (0-100).
    Considers ADTV (Average Daily Traded Value), Volume, Delivery %.
    """
    # MOCK Calculation for architectural implementation
    # In reality, fetches from Feature Store / DB
    score = 80.0
    
    # E.g. Check ADTV
    adtv = symbol_data.get('adtv_30', 0)
    if adtv > 100_000_000:
        score += 15
    elif adtv < 10_000_000:
        score -= 30
        
    return min(max(score, 0), 100)
