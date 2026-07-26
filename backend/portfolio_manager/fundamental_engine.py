import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FundamentalEngine:
    """
    Calculates fundamental metrics for a given company.
    In a live production system, this fetches from a Data Platform (e.g., FactSet, Bloomberg, or locally cached yfinance data).
    For this MVP, it generates realistic mock data based on sector averages.
    """
    
    def analyze(self, symbol: str, sector: str = "N/A") -> Dict[str, Any]:
        logger.info(f"Running Fundamental Analysis for {symbol}")
        
        # Seed random based on symbol to keep it consistent per symbol
        random.seed(hash(symbol))
        
        revenue_growth = random.uniform(-5, 45)
        eps_growth = random.uniform(-10, 50)
        roe = random.uniform(5, 35)
        roce = random.uniform(5, 40)
        debt_to_equity = random.uniform(0, 3)
        net_margin = random.uniform(2, 25)
        
        pe = random.uniform(10, 80)
        pb = random.uniform(1, 15)
        ev_ebitda = random.uniform(5, 30)
        
        # Calculate a Fundamental Score (0-100)
        score = 50
        
        if revenue_growth > 15: score += 10
        elif revenue_growth < 0: score -= 10
        
        if eps_growth > 15: score += 15
        elif eps_growth < 0: score -= 15
        
        if roe > 15: score += 10
        if debt_to_equity < 1: score += 10
        elif debt_to_equity > 2: score -= 10
        
        if pe < 20: score += 10
        elif pe > 45: score -= 10
        
        score = max(0, min(100, score))
        
        return {
            "revenue_growth": round(revenue_growth, 2),
            "profit_growth": round(eps_growth * 1.1, 2),
            "eps_growth": round(eps_growth, 2),
            "roe": round(roe, 2),
            "roce": round(roce, 2),
            "debt_to_equity": round(debt_to_equity, 2),
            "interest_coverage": round(random.uniform(2, 10), 2),
            "operating_margin": round(net_margin * 1.3, 2),
            "net_margin": round(net_margin, 2),
            "free_cash_flow": round(random.uniform(-100, 500), 2),
            "promoter_holding": round(random.uniform(30, 75), 2),
            "promoter_pledge": round(random.uniform(0, 10), 2),
            "fii_trend": random.choice(["Increasing", "Stable", "Decreasing"]),
            "dii_trend": random.choice(["Increasing", "Stable", "Decreasing"]),
            "pe": round(pe, 2),
            "pb": round(pb, 2),
            "ev_ebitda": round(ev_ebitda, 2),
            "dividend_yield": round(random.uniform(0, 4), 2),
            "fundamental_score": round(score, 2)
        }
