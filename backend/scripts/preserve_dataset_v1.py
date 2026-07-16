import pandas as pd
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PreserveV1")

DATASET_PATH = "data/ml_datasets/dataset_v1.parquet"
BACKUP_PATH = "data/ml_datasets/dataset_v1_with_outcomes.parquet"

def main():
    logger.info(f"Backing up current dataset to {BACKUP_PATH}")
    shutil.copy(DATASET_PATH, BACKUP_PATH)
    
    df = pd.read_parquet(DATASET_PATH)
    
    # Columns added by Trade Outcome Engine
    outcome_cols = [
        'Simulated_Entry_Price', 'Simulated_Exit_Price', 'MFE_Pct', 'MAE_Pct', 
        'Days_To_Target', 'Days_To_Stop', 'Trade_Outcome', 'Trade_Quality_Score',
        'Trade_Quality_Category', 'Label_Baseline', 'Label_TradeSuccess', 'Label_Ranking',
        'Target_Return_5d' # Might be from E2, let's keep it if it was from E2.
    ]
    # Actually, Target_Return_5d was E2. E3.3 added Simulated_Entry_Price etc.
    cols_to_drop = [c for c in outcome_cols if c in df.columns and c != 'Target_Return_5d']
    
    logger.info(f"Dropping columns to restore pure Feature Store: {cols_to_drop}")
    df.drop(columns=cols_to_drop, inplace=True)
    
    logger.info(f"Saving purified dataset_v1.parquet...")
    df.to_parquet(DATASET_PATH)
    logger.info("Done.")

if __name__ == "__main__":
    main()
