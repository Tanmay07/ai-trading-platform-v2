from tradability.analytics.tradability_history import SessionLocal, PromotionEvent

def handle_promotion(symbol: str, old_cat: str, new_cat: str):
    """
    Logs a promotion event when a stock moves to a higher tradability tier.
    """
    db = SessionLocal()
    event = PromotionEvent(
        symbol=symbol,
        old_category=old_cat,
        new_category=new_cat,
        event_type="PROMOTION",
        reason="Liquidity/Volume improvement detected."
    )
    db.add(event)
    db.commit()
    db.close()
