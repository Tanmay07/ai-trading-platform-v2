import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from portfolio_manager.database import SessionLocal
from portfolio_manager.models import Portfolio, Transaction, TransactionType

def import_holdings(file_path):
    print(f"Reading {file_path}...")
    
    df = pd.read_excel(file_path)
    
    # Find the row index where 'Unnamed: 1' == 'Symbol'
    header_row_idx = None
    for idx, row in df.iterrows():
        if str(row.get('Unnamed: 1')) == 'Symbol':
            header_row_idx = idx
            break
            
    if header_row_idx is None:
        print("Could not find 'Symbol' header.")
        return
        
    df = pd.read_excel(file_path, header=header_row_idx + 1)
    
    db = SessionLocal()
    
    # Get the Primary Portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.name == "Primary Portfolio").first()
    if not portfolio:
        portfolio = Portfolio(
            user_id="tenant_1",
            name="Primary Portfolio",
            currency="INR",
            base_capital=1000000.0,
            investment_objective="Growth",
            benchmark_index="NIFTY50"
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        
    # Clear existing transactions for this portfolio to avoid duplicates if re-running
    db.query(Transaction).filter(Transaction.portfolio_id == portfolio.id).delete()
    db.commit()
    
    transactions = []
    
    for idx, row in df.iterrows():
        symbol = str(row.get('Symbol'))
        if symbol == 'nan' or not symbol:
            continue
            
        qty_available = row.get('Quantity Available', 0)
        qty_pledged = row.get('Quantity Pledged (Margin)', 0)
        
        total_qty = 0
        try:
            total_qty = float(qty_available) if pd.notna(qty_available) else 0
        except ValueError:
            pass
            
        try:
            total_qty += float(qty_pledged) if pd.notna(qty_pledged) else 0
        except ValueError:
            pass
            
        avg_price = row.get('Average Price', 0)
        try:
            avg_price = float(avg_price)
        except ValueError:
            avg_price = 0
            
        if total_qty > 0 and avg_price > 0:
            transactions.append(Transaction(
                portfolio_id=portfolio.id,
                symbol=symbol,
                transaction_type=TransactionType.BUY,
                quantity=total_qty,
                price=avg_price,
                timestamp=datetime.now()
            ))
            print(f"Added {symbol}: {total_qty} @ {avg_price}")
            
    if transactions:
        db.add_all(transactions)
        db.commit()
        print(f"Successfully imported {len(transactions)} holdings into portfolio '{portfolio.name}'.")
    else:
        print("No valid holdings found to import.")
        
    db.close()

if __name__ == "__main__":
    import_holdings("/Users/tanmayadhikary/Downloads/holdings-BZS977 (3).xlsx")
