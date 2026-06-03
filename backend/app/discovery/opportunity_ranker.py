"""
Opportunity Ranker

Orchestrates the discovery engines to scan the universe, aggregate scores,
and apply the Opportunity Score formula.
"""
import asyncio
from typing import List, Dict, Any
from app.utils.logger import get_logger
from app.discovery.universe_builder import UniverseBuilder
from app.discovery.market_data_service import BatchMarketDataService
from app.discovery.fundamental_data_service import FundamentalDataService
from app.discovery.valuation_engine import ValuationEngine
from app.discovery.momentum_detector import MomentumDetector
from app.discovery.sentiment_engine import DiscoverySentimentEngine
from app.discovery.sector_strength_engine import SectorStrengthEngine
from app.discovery.growth_predictor import GrowthPredictor
from app.features.sentiment_analyzer import SentimentAnalyzer
from app.data.news_service import NewsService

class OpportunityRanker:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.universe = UniverseBuilder()
        self.market_service = BatchMarketDataService()
        self.fundamental_service = FundamentalDataService()
        self.valuation_engine = ValuationEngine()
        self.momentum_detector = MomentumDetector()
        
        # Shared instances for sentiment
        news_svc = NewsService()
        analyzer = SentimentAnalyzer()
        self.sentiment_engine = DiscoverySentimentEngine(analyzer, news_svc)
        
        self.sector_engine = SectorStrengthEngine()
        self.growth_predictor = GrowthPredictor()

    async def scan_universe(self, category: str = "all") -> List[Dict[str, Any]]:
        """
        Scans the Nifty 50 universe (for MVP) and generates Opportunity Scores.
        """
        symbols = self.universe.get_nifty_50()
        
        # Batch download historical data
        hist_data = self.market_service.download_historical_data(symbols, period="1y")
        
        opportunities = []
        
        # Process each symbol sequentially (could be async.gather for I/O bound parts)
        for symbol in symbols:
            try:
                # 1. Fundamentals
                fundamentals = self.fundamental_service.fetch_fundamentals(symbol)
                if not fundamentals:
                    continue
                
                fund_score = self.valuation_engine.compute_fundamental_score(fundamentals)
                val_score = self.valuation_engine.compute_value_score(fundamentals)
                
                # 2. Momentum
                mom_score = None
                if hist_data is not None and symbol in hist_data.columns.get_level_values('Ticker'):
                    # Extract single symbol df from multiindex
                    df = hist_data.xs(symbol, level='Ticker', axis=1)
                    mom_score = self.momentum_detector.compute_momentum_score(df)
                    
                # 3. Sector
                sec_score = self.sector_engine.compute_sector_score(symbol)
                
                # 4. Sentiment (Async)
                sent_score = await self.sentiment_engine.compute_sentiment_score(symbol)
                
                # Fallbacks if missing
                fs = fund_score["fundamental_score"] if fund_score else 50.0
                vs = val_score["value_score"] if val_score else 50.0
                ms = mom_score["momentum_score"] if mom_score else 50.0
                ss = sec_score["sector_score"] if sec_score else 50.0
                ns = sent_score["sentiment_score"] if sent_score else 50.0
                
                # 5. AI Prediction
                ai_pred = self.growth_predictor.predict_growth_probability(symbol, ms, fs, ns)
                ai_score = ai_pred["probability"] if ai_pred else 50.0
                
                # 6. Final Opportunity Score Formula
                # Opportunity Score = 0.30 × AI + 0.25 × Fund + 0.15 × Mom + 0.10 × Val + 0.10 × Sent + 0.10 × Sector
                opp_score = (0.30 * ai_score) + (0.25 * fs) + (0.15 * ms) + (0.10 * vs) + (0.10 * ns) + (0.10 * ss)
                
                opportunities.append({
                    "symbol": symbol,
                    "current_price": fundamentals.get("current_price"),
                    "opportunity_score": round(opp_score, 2),
                    "ai_score": round(ai_score, 2),
                    "fundamental_score": fs,
                    "momentum_score": ms,
                    "value_score": vs,
                    "sentiment_score": ns,
                    "sector_score": ss,
                    "sector": sec_score.get("sector") if sec_score else "Unknown",
                    "predicted_return": ai_pred.get("expected_return") if ai_pred else 0.0,
                    "confidence": ai_pred.get("confidence") if ai_pred else 0.0,
                    "all_reasons": (fund_score.get("reasons", []) if fund_score else []) +
                                   (mom_score.get("reasons", []) if mom_score else []) +
                                   (sent_score.get("reasons", []) if sent_score else [])
                })
                
            except Exception as e:
                self.logger.error(f"Error processing {symbol} in ranker: {e}")
                
        # Sort by opportunity score descending
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities
