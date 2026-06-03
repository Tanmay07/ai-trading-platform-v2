"""
Valuation Engine

Calculates fundamental scoring and value scoring for stocks.
"""
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

class ValuationEngine:
    def __init__(self):
        self.logger = get_logger(__name__)

    def compute_fundamental_score(self, fundamentals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Computes a fundamental health score (0-100).
        """
        if not fundamentals:
            return None

        score = 50.0
        reasons = []

        # Profitability (ROE)
        roe = fundamentals.get("roe")
        if roe is not None:
            if roe > 0.20:
                score += 15
                reasons.append(f"Excellent ROE ({roe*100:.1f}%)")
            elif roe > 0.15:
                score += 10
                reasons.append(f"Good ROE ({roe*100:.1f}%)")
            elif roe < 0.05:
                score -= 10
                reasons.append(f"Poor ROE ({roe*100:.1f}%)")

        # Margins
        op_margin = fundamentals.get("operating_margin")
        if op_margin is not None:
            if op_margin > 0.20:
                score += 10
                reasons.append(f"High Operating Margin ({op_margin*100:.1f}%)")
            elif op_margin < 0.05:
                score -= 5
                reasons.append(f"Low Operating Margin ({op_margin*100:.1f}%)")

        # Growth
        rev_growth = fundamentals.get("revenue_growth")
        if rev_growth is not None:
            if rev_growth > 0.15:
                score += 10
                reasons.append(f"Strong Revenue Growth ({rev_growth*100:.1f}%)")
            elif rev_growth < 0:
                score -= 15
                reasons.append("Negative Revenue Growth")

        # Balance Sheet
        debt_to_equity = fundamentals.get("debt_to_equity")
        if debt_to_equity is not None:
            # debtToEquity in yfinance is usually out of 100 (e.g., 50 means 0.5 D/E)
            de_ratio = debt_to_equity / 100.0 
            if de_ratio < 0.3:
                score += 10
                reasons.append("Low Debt to Equity")
            elif de_ratio > 1.5:
                score -= 15
                reasons.append("High Debt to Equity")

        # Clamp
        final_score = max(0, min(100, score))

        return {
            "fundamental_score": round(final_score, 2),
            "reasons": reasons
        }

    def compute_value_score(self, fundamentals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Identifies undervalued stocks and those near 52-week lows (0-100 score).
        """
        if not fundamentals:
            return None

        score = 50.0
        reasons = []

        current_price = fundamentals.get("current_price")
        low_52 = fundamentals.get("fifty_two_week_low")
        high_52 = fundamentals.get("fifty_two_week_high")
        pe_ratio = fundamentals.get("pe_ratio")

        if current_price and low_52 and high_52:
            # How close are we to the 52 week low? (0% means exactly at low, 100% means at high)
            range_52 = high_52 - low_52
            if range_52 > 0:
                percent_from_low = (current_price - low_52) / range_52
                
                if percent_from_low < 0.10: # Within 10% of 52-week low
                    score += 20
                    reasons.append("Trading very close to 52-week low")
                elif percent_from_low < 0.30:
                    score += 10
                    reasons.append("Trading in lower quartile of 52-week range")
                elif percent_from_low > 0.80:
                    score -= 10
                    reasons.append("Trading near 52-week high (lower value margin)")

        if pe_ratio is not None:
            if 0 < pe_ratio < 15:
                score += 15
                reasons.append(f"Attractive P/E Ratio ({pe_ratio:.1f})")
            elif pe_ratio > 40:
                score -= 15
                reasons.append(f"Expensive Valuation (P/E {pe_ratio:.1f})")

        final_score = max(0, min(100, score))

        return {
            "value_score": round(final_score, 2),
            "reasons": reasons
        }
