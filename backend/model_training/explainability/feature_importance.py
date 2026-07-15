import pandas as pd
import logging

logger = logging.getLogger("FeatureImportance")

def extract_global_importance(model, feature_names):
    """
    Extracts LightGBM's native feature importance (Gain).
    """
    logger.info("Extracting global feature importance...")
    importance = model.feature_importance(importance_type='gain')
    
    df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    })
    
    df = df.sort_values(by='importance', ascending=False).reset_index(drop=True)
    return df
