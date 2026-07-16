import pandas as pd
import yaml
import logging

from factor_engine.factors.price_factors import TrendFactor, RelativeStrengthFactor, BreakoutQualityFactor
from factor_engine.factors.market_factors import (
    VolatilityFactor, LiquidityFactor, MarketBreadthFactor,
    RegimeFactor, RiskFactor, MomentumFactor, InstitutionalActivityFactor
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeatureStoreV2")

class FeatureStoreV2Builder:
    def __init__(self):
        with open("config/factor_engine.yaml", "r") as f:
            self.config = yaml.safe_load(f)["factor_engine"]
            
        self.adaptive = self.config.get("adaptive_mode", False)
        
        self.factors = [
            TrendFactor(self.config['factors'], self.adaptive),
            RelativeStrengthFactor(self.config['factors'], self.adaptive),
            BreakoutQualityFactor(self.config['factors'], self.adaptive),
            VolatilityFactor(self.config['factors'], self.adaptive),
            LiquidityFactor(self.config['factors'], self.adaptive),
            MarketBreadthFactor(self.config['factors'], self.adaptive),
            RegimeFactor(self.config['factors'], self.adaptive),
            RiskFactor(self.config['factors'], self.adaptive),
            MomentumFactor(self.config['factors'], self.adaptive),
            InstitutionalActivityFactor(self.config['factors'], self.adaptive)
        ]

    def build(self):
        v2_path = self.config["dataset_v2_path"]
        v3_path = self.config["dataset_v3_path"]
        
        logger.info(f"Loading Dataset V2 from {v2_path}")
        df = pd.read_parquet(v2_path)
        
        logger.info(f"Loaded {len(df)} rows. Calculating 10 Institutional Factors...")
        
        for factor in self.factors:
            logger.info(f"Computing {factor.name}...")
            df[factor.name] = factor.calculate(df)
            
        # Update metadata
        df['Dataset_Version'] = "v3"
        df['Factor_Version'] = "v1"
        
        logger.info(f"Saving Dataset V3 to {v3_path}")
        df.to_parquet(v3_path)
        logger.info("Feature Store V2 Build Complete!")
        
if __name__ == "__main__":
    builder = FeatureStoreV2Builder()
    builder.build()
