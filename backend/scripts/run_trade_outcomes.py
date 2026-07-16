import pandas as pd
import yaml
import logging
from tqdm import tqdm
from trade_outcomes.engine.trade_replay import TradeReplayEngine
from trade_outcomes.labels.baseline_label import BaselineLabeler
from trade_outcomes.labels.trade_success_label import TradeSuccessLabeler
from trade_outcomes.labels.ranking_label import RankingLabeler
from trade_outcomes.labels.label_comparator import LabelComparator
from trade_outcomes.registry.label_registry import LabelRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradeOutcomes")

def main():
    logger.info("Loading config...")
    with open("config/trade_labels.yaml", "r") as f:
        config = yaml.safe_load(f)["trade_rules"]
        
    logger.info("Loading dataset_v1.parquet...")
    df = pd.read_parquet("data/ml_datasets/dataset_v1.parquet")
    
    # We need Open, High and Low to do trade replay. Let's check if they exist.
    if not {'Open', 'High', 'Low'}.issubset(df.columns):
        logger.info("Open/High/Low not found in dataset. Pulling from historical lake...")
        import os
        
        # Load raw data and map it
        raw_dfs = []
        # Find unique symbols
        symbols = df['symbol'].unique()
        
        for sym in tqdm(symbols, desc="Loading raw OHLCV"):
            file_path = f"data/historical_lake/historical/equities/{sym}.parquet"
            if os.path.exists(file_path):
                sym_df = pd.read_parquet(file_path)
                sym_df['symbol'] = sym
                raw_dfs.append(sym_df)
                
        if not raw_dfs:
            logger.error("No raw data found!")
            return
            
        raw_full = pd.concat(raw_dfs)
        raw_full = raw_full.reset_index().set_index(['Date', 'symbol'])
        df = df.reset_index().set_index(['Date', 'symbol'])
        
        # We need Open, High, and Low
        df['Open'] = raw_full['Open']
        df['High'] = raw_full['High']
        df['Low'] = raw_full['Low']
        df = df.reset_index().set_index('Date')
        
    logger.info("Starting Trade Replay Engine...")
    engine = TradeReplayEngine(
        holding_period=config['holding_period'],
        target_pct=config['profit_target'],
        stop_loss_pct=config['stop_loss'],
        quality_weights=config.get('quality_weights', None)
    )
    
    # Group by symbol and apply trade replay
    # We must sort by Date for each symbol
    logger.info("Replaying trades for 750 symbols...")
    df = df.reset_index()
    # Apply engine symbol by symbol
    replayed_dfs = []
    
    for sym, group in tqdm(df.groupby('symbol'), desc="Simulating Trades"):
        group = group.sort_values('Date')
        replayed_group = engine.replay_symbol_history(group)
        replayed_dfs.append(replayed_group)
        
    df = pd.concat(replayed_dfs)
    df = df.set_index('Date')
    
    logger.info("Generating Labels...")
    df['Label_Baseline'] = BaselineLabeler(target_return=5.0).generate_labels(df)
    df['Label_TradeSuccess'] = TradeSuccessLabeler().generate_labels(df)
    df['Label_Ranking'] = RankingLabeler(top_percentile=config['ranking_percentage']).generate_labels(df)
    
    logger.info("Comparing Label Strategies...")
    metrics = LabelComparator.compare(df, ['Label_Baseline', 'Label_TradeSuccess', 'Label_Ranking'])
    
    logger.info("Registering Results...")
    registry = LabelRegistry()
    version = registry.register_labels(metrics, config)
    
    logger.info(f"Successfully evaluated and registered trade outcomes under {version}.")
    
    # Save the updated dataset back so the UI can fetch MFE/MAE dists
    logger.info("Saving dataset_v1.parquet with trade outcomes...")
    df.to_parquet("data/ml_datasets/dataset_v1.parquet")
    logger.info("Done!")

if __name__ == "__main__":
    main()
