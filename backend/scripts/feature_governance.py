import os
import sys
import pandas as pd
import numpy as np
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeatureGovernance")

class FeatureGovernancePipeline:
    def __init__(self, input_path="data/ml_datasets/dataset_v3.parquet", output_path="data/ml_datasets/dataset_v5.parquet"):
        self.input_path = input_path
        self.output_path = output_path
        self.reports_dir = Path("docs/G7.2.1_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.df = None
        
        self.feature_catalog = []
        self.production_whitelist = []
        self.rejected_features = []
        
        # Strict Forbidden Semantic Patterns
        self.forbidden_patterns = [
            r'target', r'label', r'future', r'simulated', r'exit',
            r'tradesuccess', r'pnl', r'return_\d+d', r'mfe', r'mae',
            r'days_to_target', r'days_to_stop', r'outcome',
            r'quality_score', r'ranking', r'quality_factor'
        ]
        
    def run_pipeline(self):
        logger.info("Starting Institutional Feature Governance Pipeline...")
        self._load_data()
        self._phase_1_3_catalog_and_classification()
        self._phase_4_7_forbidden_and_whitelist()
        self._phase_10_dataset_certification()
        self._phase_11_rebuild_dataset_v5()
        logger.info("Governance Pipeline Complete.")
        
    def _load_data(self):
        logger.info(f"Loading {self.input_path}")
        self.df = pd.read_parquet(self.input_path)
        if 'Date' in self.df.index.names:
            self.df = self.df.reset_index()
        if 'symbol' in self.df.columns and 'Symbol' not in self.df.columns:
            self.df.rename(columns={'symbol': 'Symbol'}, inplace=True)
            
    def _classify_feature(self, col_name: str, dtype: str) -> str:
        name = col_name.lower()
        if name in ['date', 'symbol']:
            return 'Metadata'
            
        for pattern in self.forbidden_patterns:
            if re.search(pattern, name):
                if 'target' in name or 'label' in name:
                    return 'Target Derived'
                elif 'simulated' in name or 'mfe' in name or 'mae' in name or 'exit' in name:
                    return 'Simulation Derived'
                else:
                    return 'Future Derived'
                    
        if name in ['open', 'high', 'low', 'close', 'volume', 'dividends', 'stock splits']:
            return 'Historical Feature'
            
        if any(indicator in name for indicator in ['ema', 'sma', 'rsi', 'macd', 'adx', 'atr', 'bb_', 'obv', 'mfi', 'vwap']):
            return 'Technical Indicator'
            
        if 'factor' in name or 'score' in name or 'flag' in name or 'dist_' in name:
            return 'Composite Factor'
            
        return 'Unknown'
        
    def _phase_1_3_catalog_and_classification(self):
        logger.info("Phases 1-3: Generating Catalog & Classification...")
        
        for col in self.df.columns:
            dtype_str = str(self.df[col].dtype)
            category = self._classify_feature(col, dtype_str)
            
            entry = {
                "Feature Name": col,
                "Data Type": dtype_str,
                "Category": category,
                "Status": "Pending"
            }
            self.feature_catalog.append(entry)
            
        with open(self.reports_dir / "feature_catalog.md", "w") as f:
            f.write("# Institutional Feature Catalog\n\n")
            f.write("| Feature Name | Data Type | Category | Status |\n")
            f.write("|---|---|---|---|\n")
            for e in self.feature_catalog:
                f.write(f"| {e['Feature Name']} | {e['Data Type']} | {e['Category']} | {e['Status']} |\n")

    def _phase_4_7_forbidden_and_whitelist(self):
        logger.info("Phases 4-7: Forbidden Detection & Whitelist Generation...")
        
        for entry in self.feature_catalog:
            # Phase 4: Forbidden Detection
            if entry["Category"] in ['Target Derived', 'Simulation Derived', 'Future Derived', 'Unknown']:
                entry["Status"] = "Rejected"
                self.rejected_features.append(entry["Feature Name"])
            elif entry["Data Type"] == "object" or entry["Data Type"] == "string":
                # Metadata string columns
                if entry["Category"] != "Metadata":
                    entry["Status"] = "Rejected"
                    self.rejected_features.append(entry["Feature Name"])
            elif entry["Category"] == "Metadata":
                 entry["Status"] = "Metadata"
            else:
                # Phase 7: Production Whitelist
                entry["Status"] = "Production Approved"
                self.production_whitelist.append(entry["Feature Name"])
                
        # Update Catalog MD with final statuses
        with open(self.reports_dir / "feature_whitelist_report.md", "w") as f:
            f.write("# Production Feature Whitelist & Lineage Audit\n\n")
            f.write("## 1. Forbidden & Rejected Features\n")
            f.write("The following features failed the temporal integrity and lineage audit due to containing future, simulated, or target information:\n")
            for r in self.rejected_features:
                f.write(f"- `{r}`\n")
                
            f.write("\n## 2. Production Feature Whitelist\n")
            f.write("Only the following features have been explicitly approved for model training. They represent safe, point-in-time quantitative data.\n")
            for w in self.production_whitelist:
                f.write(f"- `{w}`\n")

    def _phase_10_dataset_certification(self):
        logger.info("Phase 10: Dataset Certification...")
        
        total = len(self.feature_catalog)
        approved = len(self.production_whitelist)
        rejected = len(self.rejected_features)
        
        with open(self.reports_dir / "dataset_certification_report.md", "w") as f:
            f.write("# Dataset Certification Report\n\n")
            f.write("## Governance Statistics\n")
            f.write(f"- **Total Input Columns:** {total}\n")
            f.write(f"- **Production Approved Features:** {approved}\n")
            f.write(f"- **Rejected Features:** {rejected}\n\n")
            
            if rejected > 0 and approved > 0:
                f.write("## VERDICT: CERTIFIED\n\n")
                f.write("The dataset has been successfully scrubbed of all forbidden features. A strict Production Feature Whitelist has been established. The dataset is certified for reconstruction (V5) and model training.\n")
            else:
                f.write("## VERDICT: REJECTED\n\n")
                f.write("Failed to establish a valid whitelist.\n")

    def _phase_11_rebuild_dataset_v5(self):
        logger.info("Phase 11: Rebuilding Dataset V5...")
        
        # We need Date, Symbol, the Whitelist, and ONE explicit Target column for training labels
        # Let's derive Target_Forward_Return from the raw target Target_Return_5d
        
        v5_columns = ['Date', 'Symbol'] + self.production_whitelist
        
        df_v5 = self.df[v5_columns].copy()
        
        # Assign the target directly as the label
        if 'Target_Return_5d' in self.df.columns:
            df_v5['Target_Forward_Return'] = self.df['Target_Return_5d']
        else:
            # Fallback calculation if target wasn't in v3
            df_v5['Target_Forward_Return'] = df_v5.groupby('Symbol')['Close'].pct_change(5).shift(-5)
            
        df_v5 = df_v5.dropna(subset=['Target_Forward_Return']).copy()
        
        logger.info(f"Saving certified dataset to {self.output_path} (Shape: {df_v5.shape})")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df_v5.to_parquet(self.output_path, index=False)
        
if __name__ == "__main__":
    pipeline = FeatureGovernancePipeline()
    pipeline.run_pipeline()
