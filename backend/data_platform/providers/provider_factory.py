import yaml
from typing import Optional
from pathlib import Path

from data_platform.providers.base_provider import BaseProvider
from data_platform.providers.yahoo_provider import YahooProvider

class ProviderFactory:
    """
    Factory to instantiate the correct market data provider based on configuration.
    """
    
    _providers = {
        "yahoo": YahooProvider,
        # "nse": NSEProvider # Stub for future
    }

    @classmethod
    def get_provider(cls, provider_name: Optional[str] = None) -> BaseProvider:
        """
        Returns an instance of the requested provider.
        If provider_name is None, reads from historical_data.yaml config.
        """
        if not provider_name:
            provider_name = cls._get_active_provider_from_config()
            
        provider_name = provider_name.lower()
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider '{provider_name}'. Available providers: {list(cls._providers.keys())}")
            
        return cls._providers[provider_name]()
        
    @classmethod
    def _get_active_provider_from_config(cls) -> str:
        # Resolve config path
        config_path = Path(__file__).resolve().parent.parent.parent / "config" / "historical_data.yaml"
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config.get('historical_data', {}).get('active_provider', 'yahoo')
        except FileNotFoundError:
            return "yahoo" # Default fallback
