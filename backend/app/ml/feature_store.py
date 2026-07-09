import sqlite3
import pandas as pd
import json
from typing import Dict, Any, List
from datetime import datetime
from app.config_ml import ml_config
from pathlib import Path

class FeatureStore:
    def __init__(self):
        self.db_path = ml_config.feature_store_settings.storage_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                timestamp TEXT,
                feature_data TEXT,
                target_5d REAL,
                target_hit INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        
    def store_snapshot(self, ticker: str, features: Dict[str, Any], target_5d: float = None, target_hit: int = None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Convert values to basic types for JSON serialization if needed
        clean_features = {}
        for k, v in features.items():
            try:
                clean_features[k] = float(v)
            except (ValueError, TypeError):
                clean_features[k] = str(v)
                
        c.execute('''
            INSERT INTO features (ticker, timestamp, feature_data, target_5d, target_hit)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, datetime.utcnow().isoformat(), json.dumps(clean_features), target_5d, target_hit))
        conn.commit()
        conn.close()
        
    def fetch_training_data(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM features WHERE target_hit IS NOT NULL", conn)
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
            
        # Explode feature_data
        features_list = [json.loads(x) for x in df['feature_data']]
        df_feats = pd.DataFrame(features_list)
        
        # Combine
        return pd.concat([df[['ticker', 'timestamp', 'target_5d', 'target_hit']], df_feats], axis=1)
