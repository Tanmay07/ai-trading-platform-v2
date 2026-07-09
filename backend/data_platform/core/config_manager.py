import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Simple configuration manager that loads YAML files."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(__file__).parent.parent.parent / config_dir
        
    def get_config(self, name: str) -> Dict[str, Any]:
        """Loads a config file by name (e.g. 'market_data' -> 'config/market_data.yaml')"""
        config_path = self.config_dir / f"{name}.yaml"
        if not config_path.exists():
            return {}
            
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
