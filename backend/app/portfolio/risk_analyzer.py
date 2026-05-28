"""
Risk Analyzer — evaluates risk at the individual position and portfolio levels.

Provides quantitative risk scores based on volatility, position sizing,
sector concentration, and diversification metrics.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from app.utils.logger import get_logger


class RiskAnalyzer:
    """Analyzes risk at position and portfolio level.

    Risk labels follow a simple three-tier scheme:
        - **Low** — manageable risk with adequate diversification.
        - **Medium** — elevated risk; consider position sizing.
        - **High** — significant risk; review or hedge the exposure.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    # Position-level risk
    # ------------------------------------------------------------------

    def analyze_position_risk(
        self,
        holding: dict,
        current_price: float,
        atr: float,
        volatility: float,
    ) -> dict[str, Any]:
        """Analyze risk for a single position.

        Args:
            holding: Dict with at least ``avg_buy_price`` and ``quantity``.
            current_price: Latest market price per share.
            atr: Average True Range (absolute, not %).
            volatility: Rolling daily return standard deviation.

        Returns:
            Dictionary with keys:
                - ``risk_level`` (str): Low / Medium / High.
                - ``risk_score`` (float): 0–1 composite score.
                - ``unrealized_pnl_pct`` (float): % gain/loss from avg buy.
                - ``position_size_risk`` (str): assessment of absolute exposure.
                - ``volatility_risk`` (str): assessment based on annualized vol.
                - ``drawdown_risk`` (str): how far price could fall in 1 ATR.
        """
        avg_buy = holding.get("avg_buy_price", 0.0)
        quantity = holding.get("quantity", 0)

        # --- Unrealized P&L ---
        if avg_buy > 0:
            pnl_pct = ((current_price - avg_buy) / avg_buy) * 100
        else:
            pnl_pct = 0.0

        # --- Volatility risk (annualised) ---
        annual_vol = volatility * np.sqrt(252) if 0 < volatility < 1 else volatility
        if annual_vol > 0.50:
            vol_risk = "High"
            vol_score = 1.0
        elif annual_vol > 0.30:
            vol_risk = "Medium"
            vol_score = 0.6
        else:
            vol_risk = "Low"
            vol_score = 0.3

        # --- Position size risk (market-value as a rough heuristic) ---
        market_value = current_price * quantity
        if market_value > 500_000:
            size_risk = "High"
            size_score = 0.8
        elif market_value > 200_000:
            size_risk = "Medium"
            size_score = 0.5
        else:
            size_risk = "Low"
            size_score = 0.2

        # --- Drawdown risk (1-ATR move as % of price) ---
        if current_price > 0 and atr > 0:
            atr_pct = (atr / current_price) * 100
        else:
            atr_pct = 0.0

        if atr_pct > 4.0:
            drawdown_risk = "High"
            drawdown_score = 0.9
        elif atr_pct > 2.0:
            drawdown_risk = "Medium"
            drawdown_score = 0.5
        else:
            drawdown_risk = "Low"
            drawdown_score = 0.2

        # --- Composite risk score (weighted) ---
        risk_score = float(np.clip(
            0.40 * vol_score + 0.30 * drawdown_score + 0.30 * size_score,
            0.0,
            1.0,
        ))

        # Map composite to label
        if risk_score >= 0.7:
            risk_level = "High"
        elif risk_score >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 4),
            "unrealized_pnl_pct": round(pnl_pct, 2),
            "position_size_risk": size_risk,
            "volatility_risk": vol_risk,
            "drawdown_risk": drawdown_risk,
            "atr_pct": round(atr_pct, 2),
        }

    # ------------------------------------------------------------------
    # Portfolio-level risk
    # ------------------------------------------------------------------

    def analyze_portfolio_risk(self, holdings_summary: dict) -> dict[str, Any]:
        """Analyze overall portfolio risk.

        Examines concentration, sector diversification, and aggregate metrics.

        Args:
            holdings_summary: The dict returned by
                :meth:`PortfolioService.get_portfolio_summary`.

        Returns:
            Dictionary with keys:
                - ``overall_risk`` (str): Low / Medium / High.
                - ``concentration_risk`` (str): assessment.
                - ``sector_risks`` (dict): per-sector allocation %.
                - ``largest_position_pct`` (float): % of portfolio.
                - ``top_sector`` (str): sector with highest allocation.
                - ``diversification_score`` (float): 0–1 (1 = well diversified).
                - ``holdings_count`` (int).
        """
        holdings: list[dict] = holdings_summary.get("holdings", [])
        total_mv: float = holdings_summary.get("total_market_value", 0.0)

        if not holdings or total_mv <= 0:
            return {
                "overall_risk": "High",
                "concentration_risk": "No holdings — unable to assess.",
                "sector_risks": {},
                "largest_position_pct": 0.0,
                "top_sector": "N/A",
                "diversification_score": 0.0,
                "holdings_count": 0,
            }

        # --- Position concentration ---
        position_pcts: list[float] = []
        sector_alloc: dict[str, float] = defaultdict(float)

        for h in holdings:
            mv = h.get("market_value", 0.0)
            pct = (mv / total_mv) * 100 if total_mv > 0 else 0.0
            position_pcts.append(pct)

            sector = h.get("sector", "Unknown") or "Unknown"
            sector_alloc[sector] += pct

        largest_pct = max(position_pcts) if position_pcts else 0.0

        if largest_pct > 40:
            concentration_risk = "High — single position exceeds 40% of portfolio"
        elif largest_pct > 25:
            concentration_risk = "Medium — single position exceeds 25% of portfolio"
        else:
            concentration_risk = "Low — positions are well distributed"

        # --- Sector risk ---
        sector_risks: dict[str, float] = {
            k: round(v, 2) for k, v in sorted(sector_alloc.items(), key=lambda x: -x[1])
        }
        top_sector = max(sector_alloc, key=sector_alloc.get)  # type: ignore[arg-type]

        # --- Diversification score (based on Herfindahl-Hirschman Index) ---
        hhi = sum((p / 100) ** 2 for p in position_pcts)
        n = len(position_pcts)
        # Normalised: 1/n (equal weight) → HHI_min; 1 (single stock) → HHI_max
        if n > 1:
            hhi_min = 1.0 / n
            diversification_score = float(np.clip(1.0 - (hhi - hhi_min) / (1.0 - hhi_min), 0, 1))
        else:
            diversification_score = 0.0

        # --- Overall risk ---
        if diversification_score < 0.3 or largest_pct > 40:
            overall_risk = "High"
        elif diversification_score < 0.6 or largest_pct > 25:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"

        return {
            "overall_risk": overall_risk,
            "concentration_risk": concentration_risk,
            "sector_risks": sector_risks,
            "largest_position_pct": round(largest_pct, 2),
            "top_sector": top_sector,
            "diversification_score": round(diversification_score, 4),
            "holdings_count": n,
        }
