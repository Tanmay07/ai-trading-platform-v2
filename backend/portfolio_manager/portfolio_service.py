from sqlalchemy.orm import Session
from typing import List, Dict, Any
from fastapi import HTTPException

from portfolio_manager.models import Portfolio, Transaction, TransactionType, PortfolioStatus
from portfolio_manager.schemas import PortfolioCreate, TransactionCreate, HoldingResponse, PortfolioSummaryResponse
from portfolio_manager.engine.transaction_engine import TransactionEngine
from market_data.service import MarketDataService

class PortfolioService:
    def __init__(self, db: Session, market_data_service: MarketDataService):
        self.db = db
        self.mds = market_data_service

    # --- PORTFOLIO CRUD ---
    def create_portfolio(self, user_id: str, data: PortfolioCreate) -> Portfolio:
        port = Portfolio(**data.model_dump(), user_id=user_id)
        self.db.add(port)
        self.db.commit()
        self.db.refresh(port)
        return port

    def get_portfolio(self, portfolio_id: int, user_id: str) -> Portfolio:
        port = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id).first()
        if not port:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return port

    def list_portfolios(self, user_id: str) -> List[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.status != PortfolioStatus.DELETED).all()

    # --- TRANSACTIONS ---
    def add_transaction(self, portfolio_id: int, user_id: str, data: TransactionCreate) -> Transaction:
        port = self.get_portfolio(portfolio_id, user_id)
        txn = Transaction(**data.model_dump(), portfolio_id=port.id)
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def get_transactions(self, portfolio_id: int, user_id: str) -> List[Transaction]:
        port = self.get_portfolio(portfolio_id, user_id)
        return port.transactions

    # --- HOLDINGS & LIVE VALUATION ---
    def get_holdings(self, portfolio_id: int, user_id: str) -> List[HoldingResponse]:
        transactions = self.get_transactions(portfolio_id, user_id)
        holding_states = TransactionEngine.calculate_holdings(transactions)
        
        results = []
        if not holding_states:
            return results

        # Fetch live prices in batch from MarketDataService
        symbols = list(holding_states.keys())
        # market_data_service.get_live_quotes isn't fully robust if symbols missing, but we assume it handles it
        live_quotes = {}
        for sym in symbols:
            try:
                live_quotes[sym] = self.mds.get_live_quote(sym)
            except Exception:
                live_quotes[sym] = None

        total_portfolio_value = 0.0

        for sym, state in holding_states.items():
            quote = live_quotes.get(sym)
            current_price = quote.last_price if quote else state.average_buy_price
            current_value = current_price * state.quantity
            total_portfolio_value += current_value
            
            unrealized_pnl = current_value - state.total_invested
            unrealized_pct = (unrealized_pnl / state.total_invested * 100) if state.total_invested > 0 else 0.0

            results.append(HoldingResponse(
                symbol=sym,
                company_name=sym, # TODO: fetch from symbol master
                quantity=state.quantity,
                average_buy_price=state.average_buy_price,
                total_invested=state.total_invested,
                current_price=current_price,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pct=unrealized_pct,
                last_updated=quote.timestamp if quote else None
            ))

        # Calculate portfolio weights
        if total_portfolio_value > 0:
            for r in results:
                r.portfolio_weight = (r.current_value / total_portfolio_value) * 100

        return results

    def get_summary(self, portfolio_id: int, user_id: str) -> PortfolioSummaryResponse:
        port = self.get_portfolio(portfolio_id, user_id)
        holdings = self.get_holdings(portfolio_id, user_id)
        
        total_invested = sum(h.total_invested for h in holdings)
        total_value = sum(h.current_value for h in holdings) if holdings else 0.0
        
        unrealized_pnl = total_value - total_invested
        unrealized_pct = (unrealized_pnl / total_invested * 100) if total_invested > 0 else 0.0
        
        # Calculate realized PnL from transactions
        realized_pnl = 0.0
        transactions = self.get_transactions(portfolio_id, user_id)
        # Simplified realized calculation: (sell_price - avg_buy) * qty
        # Better handled inside TransactionEngine. Let's do a basic loop for now
        # Or just return 0.0 until we fully implement Realized PnL engine.
        
        return PortfolioSummaryResponse(
            portfolio_id=port.id,
            total_portfolio_value=total_value + port.base_capital, # Cash balance is derived from capital + realized + dividends - invested
            total_invested=total_invested,
            cash_balance=port.base_capital, # Placeholder for proper cash accounting
            unrealized_pnl=unrealized_pnl,
            unrealized_pct=unrealized_pct,
            realized_pnl=realized_pnl,
            number_of_holdings=len(holdings)
        )
