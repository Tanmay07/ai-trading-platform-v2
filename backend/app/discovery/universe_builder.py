"""
Smart Universe Builder

Replaces the flat stock scanning approach with a staged filtering pipeline.
Excludes ETFs, mutual funds, penny stocks, illiquid stocks, suspended securities, etc.
"""

import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from app.utils.logger import get_logger
from app.discovery.bhavcopy_service import BhavcopyService
from app.config_yaml import trading_config

logger = get_logger(__name__)

class UniverseBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.bhavcopy_service = BhavcopyService()
        self.config = trading_config.universe_filters

    def get_candidate_universe(self, max_candidates: int = 150) -> List[Dict[str, Any]]:
        """
        Runs the staged filtering pipeline and returns a list of detailed candidate dicts.
        Pipeline:
        1. Bhavcopy (NSE Universe)
        2. Basic Validation (EQ series only)
        3. Liquidity/Volume Filter
        4. Price Filter
        5. Delivery Filter
        6. Concurrent yfinance Market Cap/Sector Filter
        """
        self.logger.info("Starting Smart Universe Builder pipeline...")
        
        try:
            df = self.bhavcopy_service.get_bhavcopy_df()
        except Exception as e:
            self.logger.error(f"Failed to fetch Bhavcopy: {e}")
            return []

        # 1. Basic Validation: Only Equities (EQ)
        # Excludes ETFs, Mutual Funds, ASM/GSM (usually BE, BZ, etc.)
        if 'SctySrs' in df.columns:
            df = df[df['SctySrs'] == 'EQ'].copy()
        elif 'SERIES' in df.columns: # fallback for older bhavcopy format
            df = df[df['SERIES'] == 'EQ'].copy()
            df = df.rename(columns={'SYMBOL': 'TckrSymb', 'CLOSE': 'ClosePric', 'TOTTRDQTY': 'TotTrdQty', 'TOTTRDVAL': 'TtlTrfVal'})
        
        # 2. Convert columns to numeric
        numeric_cols = ['ClosePric', 'TotTrdQty', 'TtlTrfVal', 'DlvryQty']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df = df.dropna(subset=['ClosePric', 'TotTrdQty'])
        
        # Calculate approximate delivery percentage if available
        if 'DlvryQty' in df.columns and 'TotTrdQty' in df.columns:
            df['DeliveryPercent'] = (df['DlvryQty'] / df['TotTrdQty']) * 100
        else:
            df['DeliveryPercent'] = 100 # Fallback
            
        # 3. Apply configurable filters
        # Price Filter
        df = df[df['ClosePric'] >= self.config.minimum_price]
        
        # Volume Filter
        df = df[df['TotTrdQty'] >= self.config.minimum_average_volume]
        
        # Delivery Filter
        df = df[df['DeliveryPercent'] >= self.config.minimum_delivery_percent]
        
        if 'TtlTrfVal' not in df.columns:
            df['TtlTrfVal'] = df['ClosePric'] * df['TotTrdQty']
            
        # Sort by Turnover (Liquidity) to get the most tradable subset before hitting yfinance
        df = df.sort_values(by='TtlTrfVal', ascending=False)
        
        # Take the top N liquid stocks to avoid spamming yfinance info endpoint
        top_df = df.head(max_candidates).copy()
        
        symbols = top_df['TckrSymb'].tolist()
        ns_symbols = [f"{sym}.NS" for sym in symbols]
        
        self.logger.info(f"Bhavcopy filtering resulted in {len(ns_symbols)} highly liquid candidates. Fetching metadata concurrently...")
        
        candidates = []
        
        def fetch_metadata(symbol, row):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                market_cap = info.get("marketCap", 0)
                
                if market_cap < self.config.minimum_market_cap:
                    return None
                    
                return {
                    "Ticker": symbol,
                    "Company": info.get("shortName", row['TckrSymb']),
                    "Sector": info.get("sector", "Unknown"),
                    "Industry": info.get("industry", "Unknown"),
                    "Market_Cap": market_cap,
                    "Liquidity_Score": row.get('TtlTrfVal', 0),
                    "Tradability_Score": row.get('TtlTrfVal', 0) * info.get("averageVolume", 1), # Simplified score
                    "Average_Volume": info.get("averageVolume", row.get('TotTrdQty', 0))
                }
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(fetch_metadata, ns_sym, row) for ns_sym, (_, row) in zip(ns_symbols, top_df.iterrows())]
            for future in futures:
                res = future.result()
                if res:
                    candidates.append(res)
                    
        # Sort final candidates by Liquidity Score
        candidates = sorted(candidates, key=lambda x: x['Liquidity_Score'], reverse=True)
        self.logger.info(f"Final Smart Universe generated with {len(candidates)} candidates.")
        
        return candidates
        
    def get_scan_universe(self, limit: int = 150) -> List[str]:
        """Backward compatibility for existing Discovery Engine."""
        candidates = self.get_candidate_universe(max_candidates=limit)
        return [c["Ticker"] for c in candidates]
