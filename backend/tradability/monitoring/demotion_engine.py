from tradability.analytics.tradability_history import SessionLocal, PromotionEvent

def handle_demotion(symbol: str, old_cat: str, new_cat: str):
    """
    Logs a demotion event when a stock drops to a lower tradability tier.
    """
    db = SessionLocal()
    event = PromotionEvent(
        symbol=symbol,
        old_category=old_cat,
        new_category=new_cat,
        event_type="DEMOTION",
        reason="Deterioration in execution metrics or liquidity."
    )
    db.add(event)
    db.commit()
    db.close()
