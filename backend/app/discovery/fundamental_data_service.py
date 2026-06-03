"""
Fundamental Data Service

Fetches and caches fundamental data from Yahoo Finance.
"""
from typing import Dict, Any, Optional
import yfinance as yf
from app.utils.logger import get_logger

class FundamentalDataService:
    def __init__(self):
        self.logger = get_logger(__name__)
        # In-memory cache for MVP. Should use Redis or DB in production.
        self._cache: Dict[str, Dict[str, Any]] = {}

    def fetch_fundamentals(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches fundamental metrics for a given symbol.
        Returns a dictionary of metrics or None if failed.
        """
        if symbol in self._cache:
            return self._cache[symbol]

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                self.logger.warning(f"No fundamental info found for {symbol}")
                return None

            fundamentals = {
                "symbol": symbol,
                "roe": info.get("returnOnEquity"),
                "roce": None, # yfinance doesn't easily provide ROCE, typically need a calc or alternate API
                "roa": info.get("returnOnAssets"),
                "operating_margin": info.get("operatingMargins"),
                "net_profit_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "pb_ratio": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "free_cash_flow": info.get("freeCashflow"),
                "operating_cash_flow": info.get("operatingCashflow"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "market_cap": info.get("marketCap"),
                "dividend_yield": info.get("dividendYield"),
                "promoter_holding": info.get("heldPercentInsiders"),
                "fii_holding": info.get("heldPercentInstitutions"),
            }

            self._cache[symbol] = fundamentals
            return fundamentals

        except Exception as e:
            self.logger.error(f"Failed to fetch fundamentals for {symbol}: {e}")
            return None
