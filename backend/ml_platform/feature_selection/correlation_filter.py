import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CorrelationFilter:
    """Removes highly correlated features to prevent multicollinearity."""
    
    @staticmethod
    def remove_highly_correlated(X: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
        """
        Removes features that have a Pearson correlation greater than `threshold` with another feature.
        """
        logger.info(f"Filtering features with correlation > {threshold}...")
        
        # Calculate correlation matrix
        corr_matrix = X.corr().abs()
        
        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find features with correlation greater than threshold
        to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
        
        if to_drop:
            logger.info(f"Dropping {len(to_drop)} highly correlated features: {to_drop}")
            return X.drop(columns=to_drop)
            
        logger.info("No highly correlated features found.")
        return X
