from alpha_registry.registry.alpha_registry import AlphaRegistry

class FactorRanking:
    """
    Ranks factors based on IC, Rank IC, and SHAP importance.
    """
    def __init__(self):
        self.registry = AlphaRegistry()
        
    def get_top_factors(self, limit: int = 10, by: str = "information_coefficient"):
        """
        Retrieves the top N factors sorted by a specific metric.
        """
        factors = self.registry.get_all_factors(status="Production")
        
        # Sort manually since we fetched all objects
        sorted_factors = sorted(factors, key=lambda x: getattr(x, by, 0.0), reverse=True)
        return sorted_factors[:limit]
        
    def get_worst_factors(self, limit: int = 10):
        factors = self.registry.get_all_factors() # Include Experimental and Deprecated
        # Find lowest ICs
        sorted_factors = sorted(factors, key=lambda x: getattr(x, "information_coefficient", 0.0))
        return sorted_factors[:limit]
