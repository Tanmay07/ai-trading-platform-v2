import pandas as pd
from feature_platform.validation.quality_validator import QualityValidator
from feature_platform.validation.leakage_detector import LeakageDetector
from feature_platform.validation.statistical_validator import StatisticalValidator
from feature_platform.validation.predictive_validator import PredictiveValidator
from feature_platform.validation.correlation_validator import CorrelationValidator
from feature_platform.validation.explainability_validator import ExplainabilityValidator
from feature_platform.storage.feature_registry import FeatureRegistry

class ValidationPipeline:
    """
    Orchestrates the entire feature validation process.
    """
    def __init__(self, target_col: str = "Target_Forward_Return"):
        self.target_col = target_col
        self.quality_val = QualityValidator()
        self.leakage_val = LeakageDetector(target_col=self.target_col)
        self.stat_val = StatisticalValidator()
        self.pred_val = PredictiveValidator(target_col=self.target_col)
        self.corr_val = CorrelationValidator()
        self.exp_val = ExplainabilityValidator()
        
        self.registry = FeatureRegistry()
        
    def validate_dataset(self, df: pd.DataFrame, feature_cols: list) -> dict:
        """
        Runs validation on all features and registers them.
        """
        all_results = {}
        
        # We need target for predictive & leakage tests
        if self.target_col not in df.columns:
            # Fallback/Mock target generation for validation testing
            if 'Close' in df.columns:
                df[self.target_col] = df.groupby('Symbol')['Close'].pct_change(5).shift(-5)
            else:
                raise ValueError("No Target or Close column available for validation target generation.")
                
        # 1. Feature-by-feature validation
        for col in feature_cols:
            if col in [self.target_col, 'Symbol', 'Date']:
                continue
                
            res = {}
            # Categorize roughly by name for explainability
            cat = "default"
            if "ema" in col.lower() or "sma" in col.lower() or "trend" in col.lower():
                cat = "trend"
            elif "rsi" in col.lower() or "macd" in col.lower() or "roc" in col.lower():
                cat = "momentum"
            elif "vol" in col.lower() or "atr" in col.lower():
                cat = "volatility"
            
            res.update(self.quality_val.validate_feature(df, col))
            res.update(self.leakage_val.validate_feature(df, col))
            res.update(self.stat_val.validate_feature(df, col))
            res.update(self.pred_val.validate_feature(df, col))
            res.update(self.exp_val.validate_feature(col, category=cat))
            
            all_results[col] = res
            
        # 2. Cross-feature validation (Correlation/Redundancy)
        corr_results = self.corr_val.validate_features(df, feature_cols)
        
        # 3. Register Features
        for col, res in all_results.items():
            if col in corr_results:
                res["redundancy_score"] = corr_results[col]["redundancy_score"]
                res["highly_correlated_with"] = corr_results[col]["highly_correlated_with"]
            else:
                res["redundancy_score"] = 100
                
            self.registry.register_feature(col, "AutoAssigned", res)
            
        return self.registry.registry
