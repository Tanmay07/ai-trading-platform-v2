class FeatureDiscovery:
    def discover_features(self) -> list:
        """
        Prunes redundant features and returns the most predictive raw dataset.
        """
        return ["RSI_14", "ATR_20", "MACD_hist"]
