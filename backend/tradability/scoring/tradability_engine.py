import yaml
import logging
from datetime import datetime

from tradability.scoring import (
    liquidity_score, volatility_score, execution_score, 
    data_quality_score, circuit_score
)
from tradability.analytics.tradability_history import TradabilityScore, SessionLocal, init_db

logger = logging.getLogger("TradabilityEngine")

class TradabilityEngine:
    def __init__(self):
        with open("config/tradability.yaml", "r") as f:
            self.config = yaml.safe_load(f)["tradability"]
        self.weights = self.config["weights"]
        self.categories = self.config["categories"]
        init_db()

    def get_category(self, score: float) -> str:
        if score >= self.categories["institutional_grade"]:
            return "Institutional Grade"
        elif score >= self.categories["highly_tradable"]:
            return "Highly Tradable"
        elif score >= self.categories["tradable"]:
            return "Tradable"
        elif score >= self.categories["monitor"]:
            return "Monitor"
        else:
            return "Restricted"

    def calculate_score(self, symbol: str, symbol_data: dict) -> dict:
        """
        Calculates the Tradability Score for a given symbol using multiple weighted components.
        """
        l_score = liquidity_score.calculate(symbol_data)
        v_score = volatility_score.calculate(symbol_data)
        e_score = execution_score.calculate(symbol_data)
        d_score = data_quality_score.calculate(symbol_data)
        c_score = circuit_score.calculate(symbol_data)

        total_score = (
            (l_score * self.weights["liquidity"]) +
            (v_score * self.weights["volatility"]) +
            (e_score * self.weights["execution"]) +
            (d_score * self.weights["data_quality"]) +
            (c_score * self.weights["circuit_behavior"])
        )

        category = self.get_category(total_score)

        return {
            "symbol": symbol,
            "total_score": round(total_score, 2),
            "category": category,
            "components": {
                "liquidity": round(l_score, 2),
                "volatility": round(v_score, 2),
                "execution": round(e_score, 2),
                "data_quality": round(d_score, 2),
                "circuit_behavior": round(c_score, 2)
            }
        }

    def process_universe(self, universe_data: dict):
        """
        Processes an entire dictionary of symbols {symbol: {data}}.
        Persists the results to the database.
        """
        db = SessionLocal()
        results = []
        for symbol, data in universe_data.items():
            result = self.calculate_score(symbol, data)
            results.append(result)
            
            # Persist to DB
            score_entry = TradabilityScore(
                symbol=symbol,
                total_score=result["total_score"],
                category=result["category"],
                liquidity_score=result["components"]["liquidity"],
                volatility_score=result["components"]["volatility"],
                execution_score=result["components"]["execution"],
                data_quality_score=result["components"]["data_quality"],
                circuit_score=result["components"]["circuit_behavior"]
            )
            db.add(score_entry)
            
        db.commit()
        db.close()
        return results
