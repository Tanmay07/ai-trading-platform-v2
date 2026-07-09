"""
Recommendation Orchestrator
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import concurrent.futures

from app.utils.logger import get_logger
from app.config_yaml import trading_config
from app.discovery.universe_builder import UniverseBuilder
from app.features.feature_pipeline import FeaturePipeline
from app.recommendations.risk_engine import RiskEngine
from app.recommendations.position_sizer import PositionSizer
from app.recommendations.stop_loss import StopLossEngine
from app.recommendations.target_engine import TargetEngine
from app.services.technical_orchestrator import TechnicalOrchestrator
from app.services.market_intelligence_orchestrator import MarketIntelligenceOrchestrator
from app.ai.ai_orchestrator import AIOrchestrator
from app.ml.ml_orchestrator import MLOrchestrator
from app.reinforcement.rl_orchestrator import RLOrchestrator
from app.portfolio.portfolio_orchestrator import PortfolioOrchestrator
from app.execution.execution_orchestrator import ExecutionOrchestrator
import asyncio

logger = get_logger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.universe_builder = UniverseBuilder()
        self.feature_pipeline = FeaturePipeline()
        self.risk_engine = RiskEngine()
        self.position_sizer = PositionSizer()
        self.stop_loss = StopLossEngine()
        self.target_engine = TargetEngine()
        self.confidence_engine = ConfidenceEngine()
        self.tech_orchestrator = TechnicalOrchestrator()
        self.mi_orchestrator = MarketIntelligenceOrchestrator()
        self.ai_orchestrator = AIOrchestrator()
        self.ml_orchestrator = MLOrchestrator()
        self.rl_orchestrator = RLOrchestrator()
        self.portfolio_orchestrator = PortfolioOrchestrator()
        self.config = trading_config.recommendation

    def _process_candidate(
        self, 
        candidate: Dict[str, Any], 
        portfolio_capital: float, 
        risk_limits: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        ticker = candidate["Ticker"]
        try:
            # We fetch 1 year of data to compute EMA200 correctly
            df = self.feature_pipeline.compute_features_for_symbol(ticker, period="1y")
            if df is None or df.empty:
                return None
                
            entry_price = df["Close"].iloc[-1]
            
            # Confidence Scoring
            confidence_data = self.confidence_engine.generate_confidence(df)
            
            # Filter low confidence right away (e.g., < 60)
            if confidence_data["confidence"] < 60:
                return None
                
            # Stop Loss calculation
            sl_data = self.stop_loss.calculate_stop_loss(df, entry_price)
            if not sl_data:
                return None
                
            # Target generation
            target_data = self.target_engine.calculate_targets(entry_price, sl_data["selected_stop"])
            
            # Position Sizing
            position_data = self.position_sizer.calculate_position(
                entry_price=entry_price,
                stop_loss=sl_data["selected_stop"],
                max_monetary_risk=risk_limits["max_monetary_risk"],
                max_capital_allocation=risk_limits["max_capital_allocation"],
                available_buying_power=risk_limits["available_buying_power"],
                portfolio_capital=portfolio_capital
            )
            
            # Require minimum quantity
            if position_data["recommended_quantity"] <= 0:
                return None

            return {
                "Ticker": ticker,
                "Company": candidate["Company"],
                "Sector": candidate["Sector"],
                "Current_Price": round(entry_price, 2),
                "Recommended_Entry": round(entry_price, 2),
                "Stop_Loss": sl_data["selected_stop"],
                "Target_1": target_data.get("target_1"),
                "Target_2": target_data.get("target_2"),
                "Target_3": target_data.get("target_3"),
                "ATR": sl_data["atr"],
                "Risk_Reward": target_data.get("reward_risk_ratio"),
                "Recommended_Quantity": position_data["recommended_quantity"],
                "Capital_Required": position_data["capital_required"],
                "Portfolio_Allocation_Percent": position_data["portfolio_percent"],
                "Confidence": confidence_data["confidence"],
                "Confidence_Grade": confidence_data["grade"],
                "Liquidity_Score": candidate["Liquidity_Score"],
                "Trend_Score": confidence_data["trend_score"],
                "Momentum_Score": confidence_data["momentum_score"],
                "Volume_Score": confidence_data["volume_score"],
                "Volatility_Score": confidence_data["volatility_score"],
                "Reason_Summary": confidence_data["reason_summary"]
            }
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            return None

    def generate_recommendations(
        self, 
        portfolio_capital: float, 
        current_exposure: float = 0.0,
        max_positions: int = None,
        sector: str = None,
        market_cap: float = None,
        confidence: float = None
    ) -> Dict[str, Any]:
        """
        Orchestrates the entire Phase 1 recommendation pipeline.
        """
        logger.info(f"Generating recommendations for capital {portfolio_capital}")
        
        # 1. Calculate global risk parameters
        risk_limits = self.risk_engine.calculate_risk_limits(portfolio_capital, current_exposure)
        
        # 2. Get Candidate Universe (Bhavcopy + Metadata)
        candidates = self.universe_builder.get_candidate_universe(max_candidates=100)
        
        # Apply pre-processing filters
        if sector:
            candidates = [c for c in candidates if c.get("Sector", "").lower() == sector.lower()]
        if market_cap:
            candidates = [c for c in candidates if c.get("Market_Cap", 0) >= market_cap]
            
        recommendations = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._process_candidate, c, portfolio_capital, risk_limits) for c in candidates]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    # Apply confidence filter
                    if confidence is None or res["Confidence"] >= confidence:
                        recommendations.append(res)
                        
        # 3. Phase 2 Technical Analysis (Bulk processing on surviving candidates)
        if recommendations:
            recommendations = self.tech_orchestrator.analyze_candidates(recommendations)
            
            # 4. Phase 3 Market Intelligence
            market_info = self.mi_orchestrator.analyze_market(
                self.tech_orchestrator.market_df, 
                getattr(self.tech_orchestrator, "df_daily_all", None)
            )
            
            # Apply adjustments to all recommendations
            for rec in recommendations:
                rec.update(market_info)
                
            # --- PHASE 5: ML INFERENCE & FEATURE STORE ---
            async def _run_ml():
                tasks = [self.ml_orchestrator.process_candidate(rec) for rec in recommendations]
                return await asyncio.gather(*tasks)
                
            ml_results = asyncio.run(_run_ml())
            
            for i, rec in enumerate(recommendations):
                rec.update(ml_results[i])
                
            # --- PHASE 4: AI SUPERVISOR & CONSENSUS ---
            async def _run_ai():
                tasks = [self.ai_orchestrator.evaluate_candidate(rec) for rec in recommendations]
                return await asyncio.gather(*tasks)
                
            ai_results = asyncio.run(_run_ai())
            
            for i, rec in enumerate(recommendations):
                rec.update(ai_results[i])
                
                # Replace legacy Confidence with AI Confidence
                rec["Confidence"] = rec.get("final_confidence", rec.get("Confidence", 0))
                rec["Recommendation_Action"] = rec.get("final_recommendation", "HOLD")
                
            # --- PHASE 6: REINFORCEMENT LEARNING ---
            async def _run_rl():
                tasks = [self.rl_orchestrator.process_candidate(rec) for rec in recommendations]
                return await asyncio.gather(*tasks)
                
            rl_results = asyncio.run(_run_rl())
            
            for i, rec in enumerate(recommendations):
                rec.update(rl_results[i])
                
                # Replace with RL Calibrated Confidence
                rec["Confidence"] = rec.get("Calibrated_Confidence", rec.get("Confidence", 0))
                
                prob_mult = market_info.get("breakout_probability_multiplier", 1.0)
                exp_mult = market_info.get("exposure_multiplier", 1.0) * rec.get("RL_Exposure_Multiplier", 1.0)
                
                adj_risk_limits = {
                    "max_monetary_risk": risk_limits["max_monetary_risk"] * exp_mult,
                    "max_capital_allocation": risk_limits["max_capital_allocation"] * exp_mult,
                    "available_buying_power": risk_limits["available_buying_power"] * exp_mult
                }
                
                position_data = self.position_sizer.calculate_position(
                    entry_price=rec["Recommended_Entry"],
                    stop_loss=rec["Stop_Loss"],
                    max_monetary_risk=adj_risk_limits["max_monetary_risk"],
                    max_capital_allocation=adj_risk_limits["max_capital_allocation"],
                    available_buying_power=adj_risk_limits["available_buying_power"],
                    portfolio_capital=portfolio_capital
                )
                rec["Recommended_Quantity"] = position_data["recommended_quantity"]
                rec["Capital_Required"] = position_data["capital_required"]
                rec["Portfolio_Allocation_Percent"] = position_data["portfolio_percent"]
                
            # Filter out non-BUY recommendations or 0 quantity
            recommendations = [r for r in recommendations if r["Recommendation_Action"] == "BUY" and r["Recommended_Quantity"] > 0]
            
            # --- PHASE 7: PORTFOLIO INTELLIGENCE ---
            # Filter and size the final recommendations
            recommendations = self.portfolio_orchestrator.filter_and_allocate(recommendations)
            
            # Phase 9: Execution (Mock sending the top 1 candidate if confident)
            if recommendations:
                top_candidate = recommendations[0]
                if top_candidate.get("Confidence", 0) > 80:
                    executor = ExecutionOrchestrator()
                    executor.process_recommendation(top_candidate)
                    
        # 5. Sort by Portfolio Fit Score -> AI Confidence -> Liquidity
        recommendations.sort(
            key=lambda x: (x.get("Portfolio_Fit_Score", 0), x.get("final_confidence", 0), x.get("Liquidity_Score", 0)),
            reverse=True
        )
        
        # 6. Limit results
        limit = max_positions if max_positions else self.config.max_count
        top_recs = recommendations[:limit]
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "market_status": "OPEN", 
            "portfolio_capital": portfolio_capital,
            "market_intelligence": market_info if 'market_info' in locals() else {},
            "recommendations": top_recs
        }
