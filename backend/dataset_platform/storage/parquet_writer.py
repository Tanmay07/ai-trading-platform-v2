import pandas as pd
import os
import yaml
import hashlib
import logging

logger = logging.getLogger("ParquetWriter")

class ParquetWriter:
    """
    Handles saving final ML datasets and generating hashes for reproducibility.
    """
    def __init__(self):
        with open("config/dataset_platform.yaml", "r") as f:
            self.config = yaml.safe_load(f)["dataset_platform"]
        self.storage_dir = self.config["storage_dir"]
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def save_dataset(self, df: pd.DataFrame, version_id: str) -> dict:
        if df.empty:
            raise ValueError("Cannot save empty dataset.")
            
        file_path = os.path.join(self.storage_dir, f"{version_id}.parquet")
        
        # Save compressed
        df.to_parquet(file_path, compression='snappy')
        
        # Generate hash of file for registry
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            
        logger.info(f"Saved dataset {version_id} to {file_path}. Hash: {file_hash}")
        
        return {
            "path": file_path,
            "hash": file_hash
        }
