import pandas as pd
import logging
from feature_platform.engine.dependency_manager import DependencyManager
import importlib

logger = logging.getLogger("FeatureEngine")

class FeatureEngine:
    def __init__(self):
        self.dependency_manager = DependencyManager()
        self._register_core_categories()
        
    def _register_core_categories(self):
        # Base independent features
        self.dependency_manager.add_category("trend_features")
        self.dependency_manager.add_category("momentum_features")
        self.dependency_manager.add_category("volume_features")
        self.dependency_manager.add_category("statistical_features")
        self.dependency_manager.add_category("time_features")
        self.dependency_manager.add_category("candlestick_features")
        
        # Dependent features
        self.dependency_manager.add_category("volatility_features", depends_on=["trend_features"])
        self.dependency_manager.add_category("breakout_features", depends_on=["volatility_features", "volume_features"])
        self.dependency_manager.add_category("relative_strength", depends_on=["momentum_features", "trend_features"])
        self.dependency_manager.add_category("market_features")
        
        # Future placeholders
        self.dependency_manager.add_category("tradability_features")
        self.dependency_manager.add_category("news_features")
        self.dependency_manager.add_category("portfolio_features")

    def generate_features_for_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the registered categories in topological order on a dataframe.
        Modifies df in place with new feature columns.
        """
        if df.empty:
            return df
            
        execution_order = self.dependency_manager.resolve_execution_order()
        
        for category in execution_order:
            try:
                module = importlib.import_module(f"feature_platform.categories.{category}")
                generator = getattr(module, "generate_features", None)
                if generator:
                    df = generator(df)
            except Exception as e:
                logger.error(f"Failed to generate features for category '{category}': {e}")
                
        return df
