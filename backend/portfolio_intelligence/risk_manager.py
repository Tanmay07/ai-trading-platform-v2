import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any

logger = logging.getLogger("RiskManager")

class RiskManager:
    """
    Calculates portfolio-level risk metrics:
    Volatility, Beta, Drawdown, VaR, and Sector Concentration.
    """
    def __init__(self, risk_free_rate: float = 0.05, var_confidence: float = 0.95):
        self.risk_free_rate = risk_free_rate
        self.var_confidence = var_confidence
        # Note: In a production system, we would load actual daily return history
        # from a timeseries DB. For the prototype, we use simplified parametric estimators.
        
    def calculate_portfolio_risk(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """
        Evaluate risk metrics for the current portfolio allocation.
        """
        if total_value <= 0 or not positions:
            return {
                "portfolio_volatility": 0.0,
                "beta": 0.0,
                "value_at_risk_95": 0.0,
                "max_drawdown": 0.0,
                "sector_concentration": {},
                "diversification_score": 100.0,
                "risk_score": 0.0
            }

        # Simulated historical returns based on AI confidence logic
        # High confidence implies lower risk for the prototype simulation
        weights = []
        volatilities = []
        betas = []
        sectors = {}
        
        for pos in positions:
            w = (pos['quantity'] * pos['entry_price']) / total_value
            weights.append(w)
            
            # Simulated volatility (inverse to confidence for demonstration)
            conf = pos.get('ai_confidence', 0.5)
            vol = 0.30 - (conf * 0.15) # Example: 15% to 30% annualized vol
            volatilities.append(vol)
            
            # Simulated beta
            beta = 1.2 - (conf * 0.4) # Example: 0.8 to 1.2
            betas.append(beta)
            
            # Sector (Assuming a mock mapping for now, ideally retrieved from DB)
            # Will use a dummy sector generation based on symbol hash for stable prototype output
            sector = self._mock_sector(pos['symbol'])
            sectors[sector] = sectors.get(sector, 0) + w
            
        weights = np.array(weights)
        volatilities = np.array(volatilities)
        betas = np.array(betas)
        
        # Simplified Portfolio Volatility (Assuming correlation=0.5 for prototype)
        corr = 0.5
        cov_matrix = np.outer(volatilities, volatilities) * corr
        np.fill_diagonal(cov_matrix, volatilities**2)
        
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        port_beta = np.dot(weights, betas)
        
        # Parametric VaR (1-day) assuming 252 trading days
        z_score = 1.645 # 95% confidence
        daily_vol = port_volatility / np.sqrt(252)
        var_95 = total_value * z_score * daily_vol
        
        # Diversification Score (Herfindahl-Hirschman Index inverse)
        hhi = sum(w**2 for w in sectors.values())
        div_score = max(0.0, (1.0 - hhi) * 100.0)
        
        # Risk Score (0-100)
        risk_score = min(100.0, port_volatility * 100.0 * 2.0)
        
        return {
            "portfolio_volatility": float(port_volatility),
            "beta": float(port_beta),
            "value_at_risk_95": float(var_95),
            "max_drawdown": float(port_volatility * 1.5), # heuristic
            "sector_concentration": sectors,
            "diversification_score": float(div_score),
            "risk_score": float(risk_score)
        }
        
    def _mock_sector(self, symbol: str) -> str:
        # Stable deterministic mock mapping
        h = sum(ord(c) for c in symbol)
        sectors = ["Financials", "Technology", "Healthcare", "Consumer", "Energy", "Industrials"]
        return sectors[h % len(sectors)]
