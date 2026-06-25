import uuid
from typing import List, Dict, Any
from app.data.s3_service import S3StorageService
from app.data.market_data_service import MarketDataService
from app.utils.helpers import get_ist_now
from app.utils.logger import get_logger

PAPER_TRADING_KEY = "portfolio/paper_trading.json"

class PaperTradingService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.s3 = S3StorageService()
        self.market_data = MarketDataService()

    def _load_portfolios(self) -> List[Dict[str, Any]]:
        data = self.s3.download_json(PAPER_TRADING_KEY)
        return data if data else []

    def _save_portfolios(self, portfolios: List[Dict[str, Any]]) -> None:
        self.s3.upload_json(PAPER_TRADING_KEY, portfolios)

    def create_paper_portfolio(self, bundle: Dict[str, Any]) -> str:
        portfolios = self._load_portfolios()
        
        portfolio_id = str(uuid.uuid4())
        
        new_portfolio = {
            "id": portfolio_id,
            "created_at": get_ist_now().isoformat(),
            "target": bundle.get("target"),
            "expected_total_profit": bundle.get("expected_total_profit"),
            "total_capital_required": bundle.get("total_capital_required"),
            "stocks": []
        }

        for stock in bundle.get("stocks", []):
            new_portfolio["stocks"].append({
                "symbol": stock["symbol"],
                "company_name": stock.get("company_name", ""),
                "quantity": stock["target_plan"]["quantity"],
                "entry_price": stock["trade_setup"]["sugg_entry"],
                "target_price": stock["trade_setup"]["exit_price"],
                "stop_loss": stock["trade_setup"]["stop_loss"]
            })

        portfolios.append(new_portfolio)
        self._save_portfolios(portfolios)
        self.logger.info(f"Created paper portfolio {portfolio_id}")
        return portfolio_id

    def get_all_paper_portfolios(self) -> List[Dict[str, Any]]:
        portfolios = self._load_portfolios()
        
        # Calculate real-time P&L for each portfolio
        for portfolio in portfolios:
            total_invested = 0
            total_current_value = 0
            
            for stock in portfolio["stocks"]:
                symbol = stock["symbol"]
                quantity = stock["quantity"]
                entry_price = stock["entry_price"]
                
                # Fetch current market data
                try:
                    info = self.market_data.get_current_price(symbol)
                    current_price = info.get("price") if info and "price" in info and info["price"] > 0 else entry_price
                except Exception:
                    current_price = entry_price
                
                stock["current_price"] = current_price
                invested = quantity * entry_price
                current_val = quantity * current_price
                
                stock["invested"] = round(invested, 2)
                stock["current_value"] = round(current_val, 2)
                stock["pnl"] = round(current_val - invested, 2)
                stock["pnl_pct"] = round((stock["pnl"] / invested) * 100, 2) if invested > 0 else 0
                
                # Check status
                if current_price >= stock["target_price"]:
                    stock["status"] = "Target Hit"
                elif current_price <= stock["stop_loss"]:
                    stock["status"] = "Stop Loss Hit"
                else:
                    stock["status"] = "Active"

                total_invested += invested
                total_current_value += current_val
            
            portfolio["total_invested"] = round(total_invested, 2)
            portfolio["total_current_value"] = round(total_current_value, 2)
            portfolio["total_pnl"] = round(total_current_value - total_invested, 2)
            portfolio["total_pnl_pct"] = round((portfolio["total_pnl"] / total_invested) * 100, 2) if total_invested > 0 else 0

        # Sort by newest first
        return sorted(portfolios, key=lambda x: x.get("created_at", ""), reverse=True)

    def delete_paper_portfolio(self, portfolio_id: str) -> bool:
        portfolios = self._load_portfolios()
        filtered_portfolios = [p for p in portfolios if p["id"] != portfolio_id]
        
        if len(portfolios) != len(filtered_portfolios):
            self._save_portfolios(filtered_portfolios)
            self.logger.info(f"Deleted paper portfolio {portfolio_id}")
            return True
        return False
