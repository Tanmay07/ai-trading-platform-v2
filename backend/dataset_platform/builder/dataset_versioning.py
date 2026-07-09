import hashlib
from datetime import datetime

class DatasetVersioning:
    """
    Generates deterministic version hashes based on the parameters used to build the dataset.
    """
    
    @staticmethod
    def generate_version_id(dataset_type: str, symbols_count: int, alphas_count: int, timestamp: datetime = None) -> str:
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        # Create a unique but deterministic string
        base_string = f"{dataset_type}_{symbols_count}_{alphas_count}_{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        # MD5 is sufficient for version identification (not for security)
        version_hash = hashlib.md5(base_string.encode()).hexdigest()[:8]
        
        return f"ds_{dataset_type}_v{version_hash}"
