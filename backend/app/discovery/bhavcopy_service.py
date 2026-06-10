"""
Bhavcopy Service

Downloads the daily NSE Bhavcopy to identify the most liquid/active stocks
in the market, acting as a dynamic filter for the deep AI engine.
"""

import os
from pathlib import Path
import pandas as pd
from datetime import date, timedelta
from typing import List
from jugaad_data.nse import bhavcopy_save

from app.utils.logger import get_logger

logger = get_logger(__name__)

class BhavcopyService:
    def __init__(self):
        # We will store the downloaded Bhavcopy CSVs locally
        self.download_dir = Path(__file__).resolve().parent.parent.parent / "data" / "bhavcopy"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def get_latest_bhavcopy_date(self) -> date:
        """Finds the most recent trading day where a Bhavcopy is available."""
        d = date.today()
        # Look back up to 10 days to handle long market holidays
        for _ in range(10):
            try:
                # Attempt to download
                # jugaad_data returns None on success, raises exception on failure (like 404 for holidays)
                bhavcopy_save(d, str(self.download_dir))
                return d
            except Exception as e:
                # If downloading fails (e.g., market holiday, weekend, or today before 6 PM), step back one day
                d -= timedelta(days=1)
                
        raise Exception("Failed to fetch NSE Bhavcopy for the last 10 days.")

    def get_top_liquid_stocks(self, limit: int = 150) -> List[str]:
        """
        Downloads the latest Bhavcopy and returns the top `limit` most actively
        traded equities by turnover (Total Traded Value).
        """
        try:
            latest_date = self.get_latest_bhavcopy_date()
            filename = f"cm{latest_date.strftime('%d%b%Y').upper()}bhav.csv"
            file_path = self.download_dir / filename
            
            logger.info(f"Using Bhavcopy from {latest_date}: {filename}")
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Filter for pure Equities ('EQ' series)
            eq_df = df[df['SctySrs'] == 'EQ'].copy()
            
            # Sort by Turnover (Total Traded Value) in descending order
            # Note: TtlTrfVal might be a string in some formats, so convert to numeric
            eq_df['TtlTrfVal'] = pd.to_numeric(eq_df['TtlTrfVal'], errors='coerce')
            eq_df = eq_df.sort_values(by='TtlTrfVal', ascending=False)
            
            # Extract the top symbols
            top_stocks = eq_df.head(limit)['TckrSymb'].tolist()
            
            # Append '.NS' for Yahoo Finance compatibility
            top_stocks_ns = [f"{symbol}.NS" for symbol in top_stocks]
            
            logger.info(f"Successfully identified {len(top_stocks_ns)} highly liquid stocks from Bhavcopy.")
            return top_stocks_ns
            
        except Exception as e:
            logger.error(f"Error extracting liquid stocks from Bhavcopy: {e}")
            # Fallback to broader universe if Bhavcopy processing fails
            return self._get_fallback_universe()
            
    def _get_fallback_universe(self) -> List[str]:
        """A broader fallback list in case Bhavcopy fails completely."""
        logger.warning("Using hardcoded fallback universe.")
        return [
            # Large Caps
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
            "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "LARSEN.NS",
            "KOTAKBANK.NS", "HINDUNILVR.NS", "AXISBANK.NS", "LT.NS", "TATAMOTORS.NS",
            "M&M.NS", "ASIANPAINT.NS", "MARUTI.NS", "TATASTEEL.NS", "SUNPHARMA.NS",
            # Growth, Mid, and Small Caps
            "MTARTECH.NS", "IDEAFORGE.NS", "ZENOTECH.NS", "HAL.NS", "MAZDOCK.NS",
            "BDL.NS", "KPITTECH.NS", "TATAELXSI.NS", "SUZLON.NS", "ZOMATO.NS",
            "PAYTM.NS", "NYKAA.NS", "PBFINTECH.NS", "DIXON.NS", "POLYCAB.NS",
            "KEI.NS", "APARINDS.NS", "RVNL.NS", "IRFC.NS", "IREDA.NS",
            "JIOFIN.NS", "BSE.NS", "CDSL.NS", "CAMS.NS", "ANGELONE.NS",
            "MCX.NS", "TITAN.NS", "TRENT.NS", "VBL.NS", "CHOLAFIN.NS",
            "AUBANK.NS", "IDFCFIRSTB.NS", "SUPREMEIND.NS", "ASTRAL.NS", "PIIND.NS",
            "SRF.NS", "TATACHEM.NS", "DEEPAKNTR.NS", "NAVINFLUOR.NS", "ESCORTS.NS",
            "EICHERMOT.NS", "TVSMOTOR.NS", "HEROMOTOCO.NS", "OLECTRA.NS", "CGPOWER.NS",
            "BHEL.NS", "SIEMENS.NS", "ABB.NS", "THERMAX.NS", "BEL.NS"
        ]
