import pandas as pd
import logging
from dataset_platform.builder.feature_joiner import FeatureJoiner
from dataset_platform.builder.dataset_versioning import DatasetVersioning
from dataset_platform.storage.parquet_writer import ParquetWriter
from dataset_platform.storage.dataset_registry import DatasetRegistry
# We will implement label_generator and validators in the next sprints, but stub imports here

logger = logging.getLogger("DatasetBuilder")

class InstitutionalDatasetBuilder:
    def __init__(self):
        self.joiner = FeatureJoiner()
        self.writer = ParquetWriter()
        self.registry = DatasetRegistry()
        self.versioning = DatasetVersioning()
        
    async def build_universe_dataset(self, symbols: list, dataset_type: str = "classification"):
        """
        Orchestrates building a dataset for the entire list of symbols.
        """
        logger.info(f"Starting {dataset_type} dataset build for {len(symbols)} symbols...")
        
        all_dfs = []
        for symbol in symbols:
            df = await self.joiner.build_symbol_dataframe(symbol)
            if df.empty:
                continue
                
            # Import label generator dynamically to avoid circular dependencies if any
            from dataset_platform.builder.label_generator import LabelGenerator
            df = LabelGenerator.generate_all(df)
            
            # Missing Handler (Preprocessing)
            from dataset_platform.preprocessing.missing_handler import MissingHandler
            df = MissingHandler().apply(df)
            
            # Drop terminal rows where target is NaN (we can't train on them)
            df = df.dropna(subset=[col for col in df.columns if col.startswith('Target_')])
            
            all_dfs.append(df)
            
        if not all_dfs:
            logger.error("Failed to build dataset: No valid data found for any symbols.")
            return None
            
        master_df = pd.concat(all_dfs)
        master_df.sort_index(inplace=True)
        
        # Generate Version
        num_features = len([col for col in master_df.columns if col not in ['Symbol', 'Open', 'High', 'Low', 'Close', 'Volume'] and not col.startswith('Target')])
        version_id = self.versioning.generate_version_id(dataset_type, len(symbols), num_features)
        
        # Save to Parquet
        save_info = self.writer.save_dataset(master_df, version_id)
        
        # Register in DB
        # TODO: Calculate actual quality score and leakage
        self.registry.register_dataset(
            version_id=version_id,
            dataset_type=dataset_type,
            rows=len(master_df),
            features=num_features,
            quality=100.0,
            path=save_info["path"],
            hash_val=save_info["hash"],
            start=master_df.index.min(),
            end=master_df.index.max()
        )
        
        logger.info(f"Dataset {version_id} built successfully.")
        return version_id
