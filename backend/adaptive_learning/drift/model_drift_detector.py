import pandas as pd
from scipy.stats import ks_2samp
import logging
from adaptive_learning.db import AdaptiveLearningDB
from datetime import datetime

import os

logger = logging.getLogger("ModelDriftDetector")

class ModelDriftDetector:
    def __init__(self, baseline_data_path: str = None):
        if baseline_data_path is None:
            baseline_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dataset_v5.parquet')
        self.baseline_data_path = baseline_data_path
        self.db = AdaptiveLearningDB()
        
    def check_drift(self):
        """
        Simulates checking for feature drift. 
        In a real scenario, this would compare the baseline training data 
        against the last 30 days of live inference data.
        """
        # For prototype, we will just return a simulated health score.
        # But we'll structure it correctly.
        try:
            df = pd.read_parquet(self.baseline_data_path)
            if 'Date' in df.index.names:
                df = df.reset_index()
            
            # Simulate historical vs recent split
            dates = sorted(df['Date'].unique())
            if len(dates) < 2:
                return
                
            split_idx = int(len(dates) * 0.8)
            historical = df[df['Date'].isin(dates[:split_idx])]
            recent = df[df['Date'].isin(dates[split_idx:])]
            
            # Check drift on a key feature
            feature = 'Close_Return_1M'
            if feature in df.columns:
                stat, p_value = ks_2samp(historical[feature].dropna(), recent[feature].dropna())
                feature_drift_score = float(stat) # Higher means more drift
            else:
                feature_drift_score = 0.05
                
            prediction_drift_score = 0.02 # Simulated
            
            retraining_recommended = feature_drift_score > 0.1
            
            today = datetime.now().strftime("%Y-%m-%d")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO model_drift (date, prediction_drift_score, feature_drift_score, retraining_recommended)
                    VALUES (?, ?, ?, ?)
                ''', (today, prediction_drift_score, feature_drift_score, retraining_recommended))
                conn.commit()
                
            return {
                "date": today,
                "prediction_drift_score": prediction_drift_score,
                "feature_drift_score": feature_drift_score,
                "retraining_recommended": retraining_recommended
            }
        except Exception as e:
            logger.error(f"Error checking drift: {e}")
            return None
