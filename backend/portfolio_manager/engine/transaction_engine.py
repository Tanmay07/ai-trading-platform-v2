from typing import List, Dict
from portfolio_manager.models import Transaction, TransactionType

class HoldingState:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0.0
        self.total_invested = 0.0
        self.average_buy_price = 0.0

    def apply_transaction(self, t: Transaction):
        if t.transaction_type == TransactionType.BUY:
            self.quantity += t.quantity
            self.total_invested += (t.quantity * t.price)
            if self.quantity > 0:
                self.average_buy_price = self.total_invested / self.quantity

        elif t.transaction_type == TransactionType.SELL:
            # Selling reduces quantity, total invested reduces proportionally.
            # Realized PnL is tracked at the portfolio level, not holding level right now.
            if self.quantity > 0:
                proportion = t.quantity / self.quantity
                self.total_invested -= (self.total_invested * proportion)
                self.quantity -= t.quantity
                if self.quantity <= 0:
                    self.quantity = 0.0
                    self.total_invested = 0.0
                    self.average_buy_price = 0.0

        elif t.transaction_type == TransactionType.BONUS:
            self.quantity += t.quantity
            if self.quantity > 0:
                self.average_buy_price = self.total_invested / self.quantity

        elif t.transaction_type == TransactionType.SPLIT:
            # E.g., 2 for 1 split means new quantity = old quantity * 2. 
            # The transaction should store the multiplier in quantity.
            # e.g., t.quantity = 2 means 2-for-1.
            self.quantity *= t.quantity
            if self.quantity > 0:
                self.average_buy_price = self.total_invested / self.quantity

        elif t.transaction_type == TransactionType.DIVIDEND:
            # Dividend doesn't change holding quantity or average buy price (unless reinvested)
            pass

        elif t.transaction_type == TransactionType.RIGHTS:
            self.quantity += t.quantity
            self.total_invested += (t.quantity * t.price)
            if self.quantity > 0:
                self.average_buy_price = self.total_invested / self.quantity


class TransactionEngine:
    @staticmethod
    def calculate_holdings(transactions: List[Transaction]) -> Dict[str, HoldingState]:
        """
        Reconstructs the holding states for a given list of transactions.
        """
        # Sort transactions by timestamp/ID to ensure chronological order
        transactions_sorted = sorted(transactions, key=lambda x: (x.timestamp, x.id))
        
        holdings: Dict[str, HoldingState] = {}
        
        for t in transactions_sorted:
            if t.symbol not in holdings:
                holdings[t.symbol] = HoldingState(t.symbol)
            holdings[t.symbol].apply_transaction(t)
            
        # Filter out zero-quantity holdings
        active_holdings = {sym: state for sym, state in holdings.items() if state.quantity > 0}
        
        return active_holdings
