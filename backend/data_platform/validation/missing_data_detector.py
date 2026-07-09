import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MissingDataDetector:
    """Detects missing trading days in time series data."""

    @staticmethod
    def detect_missing_days(df: pd.DataFrame, symbol: str, threshold_days: int = 5) -> int:
        """
        Checks for gaps in the trading days.
        Note: Weekends and public holidays are expected gaps, so we only flag large gaps.
        Returns the number of suspicious gaps found.
        """
        if df.empty or len(df) < 2:
            return 0
            
        # Ensure index is sorted
        df_sorted = df.sort_index()
        
        # Calculate time difference between consecutive rows
        time_diffs = df_sorted.index.to_series().diff()
        
        # Find gaps larger than threshold_days
        # (5 days is a safe threshold to ignore long weekends/holidays)
        suspicious_gaps = time_diffs[time_diffs > pd.Timedelta(days=threshold_days)]
        
        if not suspicious_gaps.empty:
            logger.warning(f"{symbol}: Found {len(suspicious_gaps)} large gaps in data (> {threshold_days} days).")
            for date, gap in suspicious_gaps.items():
                logger.debug(f"{symbol}: Gap of {gap.days} days ending on {date.date()}")
                
        return len(suspicious_gaps)
