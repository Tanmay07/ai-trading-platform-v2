import pandas as pd

class SectorSplitter:
    """
    Filters a dataset to only include symbols belonging to a specific sector.
    """
    def __init__(self):
        # Mock universe manager response for sectors
        self.sector_map = {
            "IT": ["INFY", "TCS", "WIPRO", "HCLTECH", "TECHM"],
            "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
            "Pharma": ["SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB"]
        }
        
    def split(self, df: pd.DataFrame, sector_name: str) -> pd.DataFrame:
        if df.empty or 'Symbol' not in df.columns:
            return pd.DataFrame()
            
        allowed_symbols = self.sector_map.get(sector_name, [])
        if not allowed_symbols:
            return pd.DataFrame()
            
        return df[df['Symbol'].isin(allowed_symbols)]
