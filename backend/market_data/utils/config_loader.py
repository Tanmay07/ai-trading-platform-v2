import yaml
from pathlib import Path

def load_market_data_config() -> dict:
    config_path = Path(__file__).parent.parent.parent / "config" / "market_data.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
