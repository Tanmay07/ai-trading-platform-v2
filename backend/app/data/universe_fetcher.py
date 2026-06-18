"""
Universe Fetcher Service
========================

Fetches the market universe (e.g. NIFTY 50) dynamically from public sources like Wikipedia,
extracts the symbols and their sectors, and caches them in AWS S3.
"""

import json
import os
import csv
from datetime import date, timedelta
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from jugaad_data.nse import bhavcopy_save

from app.data.s3_service import S3StorageService
from app.utils.logger import get_logger


class UniverseFetcherService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.s3_service = S3StorageService()
        self.cache_key = "universe_sectors.json"

    def get_full_universe(self) -> Dict[str, List[str]]:
        """
        Fetch the entire NSE universe using Bhavcopy.
        
        Returns:
            Dict mapping a dummy sector name to list of symbols (with .NS appended).
        """
        self.logger.info("Fetching full NSE universe using Bhavcopy...")
        
        # Try to find a valid bhavcopy within the last 7 days
        today = date.today()
        bhavcopy_path = None
        
        # Determine a temp download directory
        download_dir = os.path.join(os.getcwd(), "data", "temp_bhavcopy")
        os.makedirs(download_dir, exist_ok=True)

        for i in range(30, 60): # Search in the past month to avoid recent NSE 404 blocks
            check_date = today - timedelta(days=i)
            try:
                self.logger.info(f"Attempting to download Bhavcopy for {check_date}")
                bhavcopy_path = bhavcopy_save(check_date, download_dir)
                if bhavcopy_path and os.path.exists(bhavcopy_path):
                    # Verify it's actually a CSV and not a 404 HTML page
                    with open(bhavcopy_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if "DOCTYPE html" not in first_line and "SYMBOL" in first_line:
                            self.logger.info(f"Successfully downloaded valid Bhavcopy to {bhavcopy_path}")
                            break
                    # If invalid, remove it and try next
                    os.remove(bhavcopy_path)
                    bhavcopy_path = None
            except Exception as e:
                self.logger.warning(f"Bhavcopy not available for {check_date}: {e}")
                
        if not bhavcopy_path or not os.path.exists(bhavcopy_path):
            # Fallback to a hardcoded known-good date if all else fails
            try:
                fallback_date = date(2024, 1, 1)
                self.logger.info(f"Attempting hardcoded fallback date: {fallback_date}")
                bhavcopy_path = bhavcopy_save(fallback_date, download_dir)
            except Exception:
                raise ValueError("Could not download Bhavcopy. Is network down?")

        symbols = []
        try:
            with open(bhavcopy_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                # Find indices of SYMBOL and SERIES
                sym_idx = -1
                ser_idx = -1
                for i, col in enumerate(header):
                    col_strip = col.strip()
                    if col_strip == 'SYMBOL':
                        sym_idx = i
                    elif col_strip == 'SERIES':
                        ser_idx = i
                
                if sym_idx == -1 or ser_idx == -1:
                    raise ValueError("Could not find SYMBOL or SERIES column in Bhavcopy")

                for row in reader:
                    if len(row) > max(sym_idx, ser_idx):
                        if row[ser_idx].strip() == 'EQ':
                            sym = row[sym_idx].strip()
                            if sym:
                                symbols.append(f"{sym}.NS")
        except Exception as e:
            self.logger.error(f"Failed to parse Bhavcopy CSV: {e}")
            raise
            
        # Clean up the downloaded file
        try:
            os.remove(bhavcopy_path)
        except:
            pass

        if not symbols:
            raise ValueError("Parsed Bhavcopy but found no EQ symbols")

        self.logger.info(f"Successfully extracted {len(symbols)} symbols from Bhavcopy.")
        return {"NSE_UNIVERSE": symbols}

    def refresh_universe_cache(self) -> Dict[str, List[str]]:
        """
        Scrape Wikipedia and upload the sector mapping to S3.
        
        Returns:
            The scraped sector mapping dictionary.
        """
        sector_map = self.get_full_universe()
        
        if not sector_map:
            raise ValueError("Scraping returned an empty map")
            
        # Upload to S3
        self.logger.info("Uploading universe cache to S3: %s", self.cache_key)
        self.s3_service.upload_json(self.cache_key, sector_map)
        
        return sector_map
