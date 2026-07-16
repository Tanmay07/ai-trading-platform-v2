import pandas as pd
import logging

logger = logging.getLogger("DatasetValidator")

class ValidationPipeline:
    @staticmethod
    def validate_schema(df: pd.DataFrame, config: dict) -> bool:
        required_cols = [
            'Simulated_Entry_Price', 'Trade_Outcome', 'Trade_Quality_Score',
            'Label_Baseline', 'Label_TradeSuccess', 'Label_Ranking',
            'Feature_Version', 'Label_Version', 'Dataset_Version'
        ]
        
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            logger.error(f"Validation failed: Missing columns: {missing}")
            return False
            
        if 'Volume' in df.columns:
            zero_vol = (df['Volume'] == 0).sum()
            if zero_vol > 0 and not config.get('allow_missing_volume', False):
                logger.error(f"Validation failed: {zero_vol} rows with 0 volume.")
                return False
                
        symbols = df['symbol'].nunique() if 'symbol' in df.columns else 0
        min_syms = config.get('min_coverage_symbols', 700)
        if symbols < min_syms:
            logger.error(f"Validation failed: Only {symbols} symbols found. Expected at least {min_syms}.")
            return False
            
        # Check for NaNs in critical columns
        nans = df['Trade_Quality_Score'].isna().sum()
        if nans > 0:
            logger.error(f"Validation failed: {nans} NaNs in Trade_Quality_Score.")
            return False
            
        logger.info("Dataset schema and integrity validation passed.")
        return True
