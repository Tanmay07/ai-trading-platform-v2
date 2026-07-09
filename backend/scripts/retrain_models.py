import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.ml.model_manager import ModelManager
from app.config import settings

def main():
    print(f"Starting batch retraining of models with updated config:")
    print(f"- n_iter: 20")
    print(f"- ML_FORWARD_DAYS: {settings.ML_FORWARD_DAYS}")
    print(f"- ML_UP_THRESHOLD: {settings.ML_UP_THRESHOLD}")
    
    manager = ModelManager()
    
    # We will use the default watchlist for a quick demonstration
    print(f"Retraining for symbols: {settings.DEFAULT_WATCHLIST}")
    
    results = manager.train_all(settings.DEFAULT_WATCHLIST, period="2y", n_iter=20)
    
    success = [r for r in results if r.success]
    print(f"\nCompleted! successfully trained {len(success)} out of {len(results)} models.")
    
if __name__ == "__main__":
    main()
