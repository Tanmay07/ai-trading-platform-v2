"""
Market Intelligence Orchestrator
Aggregates all market intelligence services.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any
import time

from app.services.market_regime_engine import MarketRegimeEngine
from app.services.market_breadth_engine import MarketBreadthEngine
from app.services.macro_engine import MacroEngine
from app.services.fii_dii_engine import FiiDiiEngine
from app.services.institutional_activity_engine import InstitutionalActivityEngine
from app.services.volatility_engine import VolatilityEngine
from app.services.liquidity_engine import LiquidityEngine
from app.services.global_market_engine import GlobalMarketEngine
from app.services.market_health_engine import MarketHealthEngine
from app.services.market_score_engine import MarketScoreEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MarketIntelligenceOrchestrator:
    def __init__(self):
        self.regime_engine = MarketRegimeEngine()
        self.breadth_engine = MarketBreadthEngine()
        self.macro_engine = MacroEngine()
        self.fii_dii_engine = FiiDiiEngine()
        self.inst_engine = InstitutionalActivityEngine()
        self.vol_engine = VolatilityEngine()
        self.liq_engine = LiquidityEngine()
        self.global_engine = GlobalMarketEngine()
        self.health_engine = MarketHealthEngine()
        self.score_engine = MarketScoreEngine()
        
        self.macro_symbols = ["^INDIAVIX", "INR=X", "DX-Y.NYB", "^TNX", "BZ=F", "GC=F", "^GSPC", "^DJI", "^N225"]
        
    def _fetch_macro_data(self) -> pd.DataFrame:
        try:
            return yf.download(self.macro_symbols, period="2mo", interval="1d", group_by='ticker', threads=True, progress=False)
        except Exception as e:
            logger.error(f"Macro fetch failed: {e}")
            return pd.DataFrame()
            
    def analyze_market(self, df_market: pd.DataFrame, df_universe: pd.DataFrame) -> Dict[str, Any]:
        """
        df_market: Nifty 50 historical data
        df_universe: Multi-Index dataframe of all candidates
        """
        t1 = time.time()
        
        # 1. Fetch Macro Data
        df_macro = self._fetch_macro_data()
        df_vix = pd.DataFrame()
        if not df_macro.empty and getattr(df_macro.columns, 'levels', None) is not None and "^INDIAVIX" in df_macro.columns.levels[0]:
            df_vix = df_macro["^INDIAVIX"].dropna()
            
        # 2. Run Engines
        regime_res = self.regime_engine.analyze(df_market)
        breadth_res = self.breadth_engine.analyze(df_universe)
        macro_res = self.macro_engine.analyze(df_macro)
        fii_res = self.fii_dii_engine.analyze()
        inst_res = self.inst_engine.analyze()
        vol_res = self.vol_engine.analyze(df_vix)
        liq_res = self.liq_engine.analyze(df_universe)
        global_res = self.global_engine.analyze(df_macro)
        
        health_res = self.health_engine.analyze(
            breadth=breadth_res.get("breadth_score", 50),
            vol=vol_res.get("volatility_score", 50),
            liq=liq_res.get("liquidity_score", 50),
            macro=macro_res.get("macro_score", 50),
            inst=inst_res.get("institutional_activity_score", 50)
        )
        
        score_res = self.score_engine.score(
            regime_score=regime_res.get("regime_score", 50),
            breadth_score=breadth_res.get("breadth_score", 50),
            macro_score=macro_res.get("macro_score", 50),
            fii_score=fii_res.get("fii_score", 50),
            vol_score=vol_res.get("volatility_score", 50),
            liq_score=liq_res.get("liquidity_score", 50),
            global_score=global_res.get("global_score", 50)
        )
        
        logger.info(f"Market Intelligence computed in {time.time()-t1:.2f}s")
        
        return {
            **regime_res,
            **breadth_res,
            **macro_res,
            **fii_res,
            **inst_res,
            **vol_res,
            **liq_res,
            **global_res,
            **health_res,
            **score_res
        }
