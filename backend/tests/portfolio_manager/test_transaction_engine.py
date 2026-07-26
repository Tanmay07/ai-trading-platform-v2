import pytest
from datetime import datetime
from portfolio_manager.models import Transaction, TransactionType
from portfolio_manager.engine.transaction_engine import TransactionEngine

def test_transaction_engine_buy_sell():
    t1 = Transaction(id=1, symbol="RELIANCE", transaction_type=TransactionType.BUY, quantity=10, price=2000.0, timestamp=datetime(2023, 1, 1))
    t2 = Transaction(id=2, symbol="RELIANCE", transaction_type=TransactionType.SELL, quantity=5, price=2500.0, timestamp=datetime(2023, 1, 2))
    
    holdings = TransactionEngine.calculate_holdings([t1, t2])
    
    assert "RELIANCE" in holdings
    rel = holdings["RELIANCE"]
    
    assert rel.quantity == 5.0
    assert rel.average_buy_price == 2000.0
    assert rel.total_invested == 10000.0

def test_transaction_engine_split():
    t1 = Transaction(id=1, symbol="TCS", transaction_type=TransactionType.BUY, quantity=10, price=3000.0, timestamp=datetime(2023, 1, 1))
    t2 = Transaction(id=2, symbol="TCS", transaction_type=TransactionType.SPLIT, quantity=2, price=0.0, timestamp=datetime(2023, 1, 2)) # 2-for-1 split
    
    holdings = TransactionEngine.calculate_holdings([t1, t2])
    
    assert "TCS" in holdings
    tcs = holdings["TCS"]
    
    assert tcs.quantity == 20.0
    assert tcs.average_buy_price == 1500.0
    assert tcs.total_invested == 30000.0
