"""
Universe Fetcher Service
========================

Fetches the market universe (e.g. NIFTY 50) dynamically from public sources like Wikipedia,
extracts the symbols and their sectors, and caches them in AWS S3.
"""

import json
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from app.data.s3_service import S3StorageService
from app.utils.logger import get_logger


class UniverseFetcherService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.s3_service = S3StorageService()
        self.cache_key = "universe_sectors.json"

    def scrape_nifty50_wiki(self) -> Dict[str, List[str]]:
        """
        Scrape the NIFTY 50 constituents from Wikipedia.
        
        Returns:
            Dict mapping sector name to list of symbols (with .NS appended).
        """
        url = "https://en.wikipedia.org/wiki/NIFTY_50"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        self.logger.info("Scraping NIFTY 50 from %s", url)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the constituents table
            tables = soup.find_all('table', {'id': 'constituents'})
            if not tables:
                tables = soup.find_all('table', {'class': 'wikitable'})
                
            if not tables:
                raise ValueError("Could not find the constituents table on Wikipedia")
                
            # Iterate to find the correct table
            sector_map: Dict[str, List[str]] = {}
            for table in tables:
                head = [th.text.strip() for th in table.find_all('th')]
                
                if 'Symbol' in head:
                    sym_idx = head.index('Symbol')
                    
                    # Find Sector column
                    sector_idx = -1
                    for j, h in enumerate(head):
                        if 'Sector' in h:
                            sector_idx = j
                            break
                            
                    for row in table.find_all('tr')[1:]:
                        cols = row.find_all('td')
                        if len(cols) > sym_idx:
                            sym = cols[sym_idx].text.strip()
                            sec = cols[sector_idx].text.strip() if sector_idx != -1 else "Unknown"
                            
                            # Standardize sector names slightly
                            sec = sec.replace("[15]", "").replace("[16]", "").strip()
                            
                            if sym:
                                symbol_ns = f"{sym}.NS"
                                if sec not in sector_map:
                                    sector_map[sec] = []
                                sector_map[sec].append(symbol_ns)
                    
                    if sector_map:
                        self.logger.info("Successfully scraped %d sectors", len(sector_map))
                        return sector_map

            raise ValueError("Found tables but 'Symbol' column was missing")
            
        except Exception as exc:
            self.logger.error("Failed to scrape NIFTY 50: %s", exc, exc_info=True)
            raise

    def refresh_universe_cache(self) -> Dict[str, List[str]]:
        """
        Scrape Wikipedia and upload the sector mapping to S3.
        
        Returns:
            The scraped sector mapping dictionary.
        """
        sector_map = self.scrape_nifty50_wiki()
        
        if not sector_map:
            raise ValueError("Scraping returned an empty map")
            
        # Upload to S3
        self.logger.info("Uploading universe cache to S3: %s", self.cache_key)
        self.s3_service.upload_json(self.cache_key, sector_map)
        
        return sector_map
