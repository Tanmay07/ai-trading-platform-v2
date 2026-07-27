import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class BhavcopyLoader:
    """
    Placeholder for downloading and parsing daily NSE Bhavcopy files.
    This allows bulk daily incremental updates across all symbols rather than
    querying Yahoo Finance for 2,000 symbols individually.
    """
    
    def fetch_bhavcopy(self, date: datetime) -> pd.DataFrame:
        """
        Fetches the bhavcopy CSV for a specific date from NSE website.
        """
        logger.info(f"Fetching Bhavcopy for {date.strftime('%Y-%m-%d')}...")
        from jugaad_data.nse import bhavcopy_save
        import os
        from datetime import timedelta
        
        dest_dir = "data/temp_bhavcopy"
        os.makedirs(dest_dir, exist_ok=True)
        
        target_date = date.date() if isinstance(date, datetime) else date
        valid_bhavcopy_path = None
        
        # Try finding the bhavcopy for the target date or stepping back up to 7 days
        for _ in range(7):
            if target_date.weekday() < 5:
                try:
                    file_path = bhavcopy_save(target_date, dest_dir)
                    with open(file_path, 'r') as f:
                        header = f.read(20)
                        if "<html" not in header.lower() and "<!doctype" not in header.lower():
                            valid_bhavcopy_path = file_path
                            break
                except Exception as e:
                    pass
            target_date -= timedelta(days=1)
            
        if not valid_bhavcopy_path:
            logger.error(f"Could not find a valid Bhavcopy near {date.strftime('%Y-%m-%d')}.")
            return pd.DataFrame()
            
        df = pd.read_csv(valid_bhavcopy_path)
        
        # Standardize columns based on old vs new format
        if 'SctySrs' in df.columns and 'TckrSymb' in df.columns:
            df = df[df['SctySrs'] == 'EQ'].copy()
            df.rename(columns={
                'TckrSymb': 'Symbol',
                'OpnPric': 'Open',
                'HghPric': 'High',
                'LwPric': 'Low',
                'ClsPric': 'Close',
                'TtlTradgVol': 'Volume'
            }, inplace=True)
        else:
            df = df[df['SERIES'] == 'EQ'].copy()
            df.rename(columns={
                'SYMBOL': 'Symbol',
                'OPEN': 'Open',
                'HIGH': 'High',
                'LOW': 'Low',
                'CLOSE': 'Close',
                'TOTTRDQTY': 'Volume'
            }, inplace=True)
            
        # Ensure we have the required columns
        req_cols = ['Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
        if all(c in df.columns for c in req_cols):
            return df[req_cols]
        else:
            logger.error("Bhavcopy DataFrame missing required columns.")
            return pd.DataFrame()
