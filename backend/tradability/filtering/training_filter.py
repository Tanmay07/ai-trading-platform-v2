import yaml

with open("config/tradability.yaml", "r") as f:
    config = yaml.safe_load(f)["tradability"]

def is_eligible_for_training(score: float, category: str) -> bool:
    """
    Checks if a stock meets the minimum configured threshold for ML model training.
    """
    if score >= config["training"]["min_score"] and category not in ["Restricted", "Monitor"]:
        return True
    return False

def filter_dataset(dataset: list) -> list:
    """
    Filters a list of dataset rows, retaining only those eligible for training.
    Assumes each row dict has a 'tradability_score' and 'tradability_category'.
    """
    return [row for row in dataset if is_eligible_for_training(row.get("tradability_score", 0), row.get("tradability_category", "Restricted"))]
