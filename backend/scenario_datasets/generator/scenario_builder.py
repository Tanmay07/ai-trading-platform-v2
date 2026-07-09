import pandas as pd
import logging
from dataset_platform.storage.dataset_registry import DatasetRegistry
from dataset_platform.builder.dataset_versioning import DatasetVersioning
from scenario_datasets.generator.scenario_registry import ScenarioRegistry
from scenario_datasets.segmentation.market_regime import MarketRegimeSplitter
from scenario_datasets.segmentation.sector_split import SectorSplitter
from scenario_datasets.segmentation.volatility_split import VolatilitySplitter
from scenario_datasets.segmentation.event_split import EventSplitter
from scenario_datasets.validation.scenario_validator import ScenarioValidator

logger = logging.getLogger("ScenarioBuilder")

class ScenarioBuilder:
    def __init__(self):
        self.master_registry = DatasetRegistry()
        self.scenario_registry = ScenarioRegistry()
        self.validator = ScenarioValidator()
        self.versioning = DatasetVersioning()
        
    def _save_and_register(self, df: pd.DataFrame, parent_id: str, category: str, name: str):
        val = self.validator.validate(df)
        if not val["valid"]:
            logger.warning(f"Scenario {category}/{name} failed validation: {val['reason']}")
            return
            
        # In a real environment, we'd save to parquet here and get the hash.
        # We will mock the hash and path since this is a demonstration of the registry logic.
        num_features = len(df.columns)
        num_symbols = df['Symbol'].nunique()
        version_id = self.versioning.generate_version_id(f"scenario_{name}", num_symbols, num_features)
        
        self.scenario_registry.register_scenario(
            version_id=version_id,
            parent_id=parent_id,
            category=category,
            name=name,
            rows=len(df),
            symbols=num_symbols,
            quality=val["score"],
            path=f"mock_path/{version_id}.parquet",
            hash_val=f"mock_hash_{version_id}"
        )
        logger.info(f"Registered Scenario: {category} / {name} (Rows: {len(df)})")
        
    def build_all_scenarios(self, parent_version_id: str, df: pd.DataFrame):
        """
        Takes a master dataset and spins off all configured specialized scenarios.
        """
        logger.info(f"Building scenarios from Master Dataset: {parent_version_id}")
        
        # Regimes
        regime_splitter = MarketRegimeSplitter()
        for regime in ["bull", "bear"]:
            sub_df = regime_splitter.split(df, regime)
            self._save_and_register(sub_df, parent_version_id, "Regime", regime.capitalize())
            
        # Sectors
        sector_splitter = SectorSplitter()
        for sector in ["IT", "Banking", "Pharma"]:
            sub_df = sector_splitter.split(df, sector)
            self._save_and_register(sub_df, parent_version_id, "Sector", sector)
            
        # Volatility
        vol_splitter = VolatilitySplitter()
        for vol in ["high", "low"]:
            sub_df = vol_splitter.split(df, vol)
            self._save_and_register(sub_df, parent_version_id, "Volatility", f"{vol.capitalize()} Vol")
            
        # Events
        evt_splitter = EventSplitter()
        for evt in ["budget"]:
            sub_df = evt_splitter.split(df, evt)
            self._save_and_register(sub_df, parent_version_id, "Event", evt.capitalize())
            
        logger.info("Scenario Generation Complete.")
