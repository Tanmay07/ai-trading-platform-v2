class FeatureRegistry:
    """
    Maintains a catalog of all ~200 generated features and their metadata.
    """
    def __init__(self):
        self.features = {
            "EMA_20": {"version": "1.0", "category": "trend", "description": "20-day Exponential Moving Average"},
            "RSI_14": {"version": "1.0", "category": "momentum", "description": "14-day Relative Strength Index"},
            "ATR_14": {"version": "1.0", "category": "volatility", "description": "14-day Average True Range"},
            "OBV": {"version": "1.0", "category": "volume", "description": "On-Balance Volume"},
            # (In a real system, we'd dynamically register this from docstrings or decorators)
        }
        
    def get_catalog(self) -> dict:
        return self.features
        
    def register_feature(self, name: str, version: str, category: str, desc: str):
        self.features[name] = {
            "version": version,
            "category": category,
            "description": desc
        }
