"""
Technical Orchestrator
Coordinates bulk fetching and sequential analysis for Phase 2.
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
import time

from app.services.multi_timeframe_engine import MultiTimeframeEngine
from app.services.relative_strength_engine import RelativeStrengthEngine
from app.services.sector_rotation_engine import SectorRotationEngine
from app.services.breakout_pattern_engine import BreakoutPatternEngine
from app.services.price_action_engine import PriceActionEngine
from app.services.vwap_engine import VWAPEngine
from app.services.support_resistance_engine import SupportResistanceEngine
from app.services.breakout_score_engine import BreakoutScoreEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TechnicalOrchestrator:
    def __init__(self):
        self.mtf_engine = MultiTimeframeEngine()
        self.rs_engine = RelativeStrengthEngine()
        self.sector_engine = SectorRotationEngine()
        self.pattern_engine = BreakoutPatternEngine()
        self.pa_engine = PriceActionEngine()
        self.vwap_engine = VWAPEngine()
        self.sr_engine = SupportResistanceEngine()
        self.score_engine = BreakoutScoreEngine()
        
        self.market_df = None
        self.sector_dfs = {}
        
    def _bulk_download(self, tickers: List[str], period: str, interval: str) -> pd.DataFrame:
        """Download multiple tickers concurrently using yfinance."""
        if not tickers:
            return pd.DataFrame()
            
        try:
            return yf.download(tickers, period=period, interval=interval, group_by='ticker', threads=True, progress=False)
        except Exception as e:
            logger.error(f"Bulk download failed: {e}")
            return pd.DataFrame()
            
    def prepare_market_context(self, candidates: List[Dict[str, Any]]) -> pd.DataFrame:
        """Fetch market benchmark and generate synthetic sector indices."""
        t1 = time.time()
        
        # 1. Fetch Nifty 50 (Market)
        self.market_df = yf.download("^NSEI", period="1y", interval="1d", progress=False)
        
        # 2. Extract sectors from candidates
        sectors = {}
        for c in candidates:
            sec = c.get("Sector", "Unknown")
            if sec not in sectors:
                sectors[sec] = []
            sectors[sec].append(c["Ticker"])
            
        # 3. Create Synthetic Sector Indices by averaging daily returns of top candidates in each sector
        all_tickers = [c["Ticker"] for c in candidates]
        
        # Fetch daily data for all candidates
        df_daily_all = self._bulk_download(all_tickers, period="1y", interval="1d")
        
        for sec, syms in sectors.items():
            valid_syms = []
            # yfinance returns single index columns if only 1 ticker is passed
            if len(all_tickers) == 1:
                valid_syms = all_tickers if not df_daily_all.empty else []
            else:
                valid_syms = [s for s in syms if s in df_daily_all.columns.levels[0]]
                
            if not valid_syms:
                continue
                
            df_sec = pd.DataFrame()
            closes = []
            for s in valid_syms:
                if len(all_tickers) == 1:
                    if 'Close' in df_daily_all.columns:
                        closes.append(df_daily_all['Close'])
                else:
                    if s in df_daily_all and 'Close' in df_daily_all[s]:
                        closes.append(df_daily_all[s]['Close'])
                    
            if closes:
                df_sec['Close'] = pd.concat(closes, axis=1).mean(axis=1)
                self.sector_dfs[sec] = df_sec
                
        # 4. Pre-calculate sector ranks
        self.sector_engine.pre_calculate_ranks(self.sector_dfs, self.market_df)
        
        logger.info(f"Prepared market context in {time.time()-t1:.2f}s")
        return df_daily_all
        
    def _extract_df(self, df_multi: pd.DataFrame, ticker: str, single: bool = False) -> pd.DataFrame:
        if df_multi.empty:
            return pd.DataFrame()
            
        if single:
            return df_multi.dropna()
            
        if ticker in df_multi.columns.levels[0]:
            df = df_multi[ticker].dropna()
            return df
        return pd.DataFrame()

    def analyze_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        tickers = [c["Ticker"] for c in candidates]
        is_single = len(tickers) == 1
        
        # 1. Prepare Market & Sectors, and get daily data
        self.df_daily_all = self.prepare_market_context(candidates)
        
        # 2. Bulk download Weekly and 1H data
        df_weekly_all = self._bulk_download(tickers, period="2y", interval="1wk")
        df_1h_all = self._bulk_download(tickers, period="1mo", interval="1h")
        
        results = []
        for candidate in candidates:
            ticker = candidate["Ticker"]
            sector = candidate.get("Sector", "Unknown")
            
            df_d = self._extract_df(self.df_daily_all, ticker, is_single)
            df_wk = self._extract_df(df_weekly_all, ticker, is_single)
            df_1h = self._extract_df(df_1h_all, ticker, is_single)
            
            # Approximate 4H from 1H
            df_4h = pd.DataFrame()
            if not df_1h.empty:
                # Safe resample
                try:
                    df_4h = df_1h.resample('4h').agg({
                        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
                    }).dropna()
                except Exception:
                    pass
                
            dfs = {"1wk": df_wk, "1d": df_d, "4h": df_4h, "1h": df_1h}
            
            # Run Engines
            mtf_res = self.mtf_engine.analyze(dfs)
            rs_res = self.rs_engine.analyze(df_d, self.market_df, self.sector_dfs.get(sector))
            sector_res = self.sector_engine.analyze(sector)
            patterns = self.pattern_engine.analyze(df_d)
            pa_res = self.pa_engine.analyze(df_d)
            vwap_res = self.vwap_engine.analyze(df_d, df_1h)
            sr_res = self.sr_engine.analyze(df_d)
            
            best_pattern = patterns[0] if patterns else {"Pattern_Name": "None", "Pattern_Quality": 0}
            
            # Composite Score
            score_res = self.score_engine.score(
                mtf_score=mtf_res.get("mtf_score", 0),
                rs_score=rs_res.get("rs_score", 0),
                pattern_quality=best_pattern.get("Pattern_Quality", 0),
                sector_score=sector_res.get("sector_score", 0),
                price_action_score=pa_res.get("price_action_score", 0),
                vwap_score=vwap_res.get("vwap_score", 0),
                support_dist=sr_res.get("distance_to_support", 0)
            )
            
            # Compile Reason
            reasons = []
            if mtf_res.get("mtf_score", 0) > 70: reasons.append("Strong MTF Trend")
            if best_pattern["Pattern_Name"] != "None": reasons.append(best_pattern["Pattern_Name"])
            if rs_res.get("rs_score", 0) > 70: reasons.append("High RS")
            if sector_res.get("sector_rank", 99) <= 3: reasons.append(f"Sector Rank #{sector_res['sector_rank']}")
            if vwap_res.get("vwap_score", 0) > 60: reasons.append("VWAP Support")
            
            tech_analysis = {
                **mtf_res,
                **rs_res,
                **sector_res,
                **pa_res,
                **vwap_res,
                **sr_res,
                **score_res,
                "Pattern_Name": best_pattern["Pattern_Name"],
                "Technical_Summary": ", ".join(reasons) if reasons else "Neutral setup"
            }
            
            candidate.update(tech_analysis)
            results.append(candidate)
            
        return results
