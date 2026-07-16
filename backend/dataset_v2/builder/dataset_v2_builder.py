import pandas as pd
import yaml
import logging
import datetime
from tqdm import tqdm

from trade_outcomes.engine.trade_replay import TradeReplayEngine
from trade_outcomes.labels.baseline_label import BaselineLabeler
from trade_outcomes.labels.trade_success_label import TradeSuccessLabeler
from trade_outcomes.labels.ranking_label import RankingLabeler

from dataset_v2.builder.validation_pipeline import ValidationPipeline
from dataset_v2.metadata.statistics_generator import StatisticsGenerator
from dataset_v2.registry.dataset_registry import DatasetRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatasetV2Builder")

class DatasetV2Builder:
    def __init__(self):
        with open("config/dataset_v2.yaml", "r") as f:
            self.config = yaml.safe_load(f)["dataset_v2"]
            
        with open("config/trade_labels.yaml", "r") as f:
            self.trade_config = yaml.safe_load(f)["trade_rules"]
            
        self.registry = DatasetRegistry(self.config["paths"]["registry"])
        
    def _fetch_missing_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        if not {'Open', 'High', 'Low'}.issubset(df.columns):
            logger.info("Open/High/Low not found in dataset. Pulling from historical lake...")
            import os
            raw_dfs = []
            symbols = df['symbol'].unique()
            for sym in tqdm(symbols, desc="Loading raw OHLCV"):
                file_path = f"data/historical_lake/historical/equities/{sym}.parquet"
                if os.path.exists(file_path):
                    sym_df = pd.read_parquet(file_path)
                    sym_df['symbol'] = sym
                    raw_dfs.append(sym_df)
            if not raw_dfs:
                return df
            raw_full = pd.concat(raw_dfs).reset_index().set_index(['Date', 'symbol'])
            df = df.reset_index().set_index(['Date', 'symbol'])
            df['Open'] = raw_full['Open']
            df['High'] = raw_full['High']
            df['Low'] = raw_full['Low']
            return df.reset_index().set_index('Date')
        return df

    def build(self):
        logger.info(f"Loading V1 Feature Store from {self.config['paths']['v1_source']}...")
        df = pd.read_parquet(self.config['paths']['v1_source'])
        df = self._fetch_missing_ohlcv(df)
        
        logger.info("Running Trade Replay Engine...")
        engine = TradeReplayEngine(
            holding_period=self.trade_config['holding_period'],
            target_pct=self.trade_config['profit_target'],
            stop_loss_pct=self.trade_config['stop_loss'],
            quality_weights=self.trade_config.get('quality_weights', None)
        )
        
        df = df.reset_index()
        replayed_dfs = []
        for sym, group in tqdm(df.groupby('symbol'), desc="Simulating Trades"):
            group = group.sort_values('Date')
            replayed_dfs.append(engine.replay_symbol_history(group))
        df = pd.concat(replayed_dfs).set_index('Date')
        
        logger.info("Generating Labels...")
        df['Label_Baseline'] = BaselineLabeler(target_return=5.0).generate_labels(df)
        df['Label_TradeSuccess'] = TradeSuccessLabeler().generate_labels(df)
        df['Label_Ranking'] = RankingLabeler(top_percentile=self.trade_config['ranking_percentage']).generate_labels(df)
        
        logger.info("Injecting Lineage Metadata...")
        gen_time = datetime.datetime.utcnow().isoformat()
        dataset_version = f"DS-V2-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        df['Feature_Version'] = self.config['lineage']['feature_version']
        df['Label_Version'] = self.config['lineage']['label_version']
        df['Trade_Engine_Version'] = self.config['lineage']['trade_engine_version']
        df['Feature_Generation_Timestamp'] = gen_time
        df['Dataset_Version'] = dataset_version
        
        logger.info("Validating Dataset V2 Schema...")
        if not ValidationPipeline.validate_schema(df, self.config['validation']):
            logger.error("Dataset validation failed. Aborting build.")
            return
            
        logger.info("Generating Statistics...")
        stats = StatisticsGenerator.generate_stats(df)
        
        logger.info(f"Saving Dataset V2 to {self.config['paths']['v2_output']}...")
        df.to_parquet(self.config['paths']['v2_output'])
        
        logger.info("Registering Dataset V2...")
        self.registry.register_dataset(
            version_id=dataset_version,
            metadata={
                "lineage": self.config['lineage'],
                "statistics": stats,
                "file_path": self.config['paths']['v2_output']
            }
        )
        
        logger.info(f"Dataset V2 Build Complete! Version: {dataset_version}")

if __name__ == "__main__":
    DatasetV2Builder().build()
