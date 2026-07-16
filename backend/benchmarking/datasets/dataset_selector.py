import pandas as pd
import yaml
import logging

logger = logging.getLogger("DatasetSelector")

class DatasetSelector:
    def __init__(self):
        with open("config/benchmarking.yaml", "r") as f:
            self.config = yaml.safe_load(f)["benchmarking"]
            
        self.dataset_path = self.config["dataset_path"]
        
        self.factors = [
            "Trend_Factor", "Relative_Strength_Factor", "Breakout_Quality_Factor",
            "Volatility_Factor", "Liquidity_Factor", "Market_Breadth_Factor",
            "Regime_Factor", "Risk_Factor", "Momentum_Factor", "Institutional_Activity_Factor"
        ]
        
        # Meta and target cols to preserve
        self.preserve_cols = [
            'symbol', 'Date', 'Target_Breakout_Success', 'Target_Return_5d'
        ]
        
    def load_mode(self, mode: str) -> pd.DataFrame:
        """
        Loads the dataset and filters columns based on the mode.
        mode in ['raw', 'factors', 'hybrid']
        """
        logger.info(f"Loading Dataset V3 in '{mode}' mode...")
        df = pd.read_parquet(self.dataset_path)
        
        # Filter down the dataset size if sample_size is set (for fast dev benchmarking)
        sample_size = self.config.get("sample_size")
        if sample_size and sample_size < len(df):
            logger.info(f"Subsampling dataset to {sample_size} rows for rapid benchmarking...")
            # We must maintain time-series structure, so take the last N rows
            df = df.sort_values('Date').tail(sample_size).copy()
            
        # Determine the columns to drop
        # Raw = drop factors
        # Factors = drop all numeric features that aren't factors/meta
        # Hybrid = keep all
        
        if mode == 'raw':
            cols_to_drop = [f for f in self.factors if f in df.columns]
            return df.drop(columns=cols_to_drop)
            
        elif mode == 'factors':
            keep_cols = set(self.factors + self.preserve_cols)
            # Find all other numeric cols that are NOT in keep_cols and drop them
            cols_to_drop = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in keep_cols]
            return df.drop(columns=cols_to_drop)
            
        elif mode == 'hybrid':
            return df
            
        else:
            raise ValueError(f"Unknown mode: {mode}")
