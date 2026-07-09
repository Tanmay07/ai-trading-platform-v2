from alpha_registry.registry.alpha_registry import AlphaRegistry
import yaml

class AlphaSelector:
    """
    Provides the best feature list to downstream consumers like DatasetBuilder.
    """
    def __init__(self):
        self.registry = AlphaRegistry()
        with open("config/alpha_registry.yaml", "r") as f:
            self.config = yaml.safe_load(f)["alpha_registry"]["thresholds"]
            
    def get_production_features(self) -> list:
        """
        Returns only the names of features marked as 'Production' or 'Experimental' 
        that meet minimum IC requirements.
        """
        factors = self.registry.get_all_factors()
        
        selected = []
        for factor in factors:
            if factor.status == "Deprecated" or factor.status == "Archived":
                continue
                
            # Allow Experimental freely to give them a chance to earn importance
            if factor.status == "Experimental":
                selected.append(factor.name)
                continue
                
            # For Production, enforce thresholds strictly
            if factor.information_coefficient >= self.config["min_ic_production"]:
                selected.append(factor.name)
                
        return selected
