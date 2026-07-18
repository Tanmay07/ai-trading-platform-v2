import lightgbm as lgb
import logging

logger = logging.getLogger("LGBMTradeQualityRegressor")

class LGBMTradeQualityRegressor:
    """
    Research-only model to predict Trade_Quality_Score directly.
    """
    def __init__(self, params: dict = None):
        self.default_params = {
            'objective': 'regression',
            'metric': ['rmse', 'mae'],
            'learning_rate': 0.03,
            'num_leaves': 64,
            'max_depth': 8,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        
        self.params = {**self.default_params, **(params or {})}
        self.model = None

    def train(self, X_train, y_train, X_val, y_val, num_boost_round=500, early_stopping_rounds=50):
        logger.info("Starting LightGBM Regression training (Research Only)...")
        
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        callbacks = [
            lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=True),
            lgb.log_evaluation(period=50)
        ]
        
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=num_boost_round,
            valid_sets=[train_data, val_data],
            valid_names=['train', 'val'],
            callbacks=callbacks
        )
        
        logger.info(f"Regression training complete. Best iteration: {self.model.best_iteration}")
        return self.model

    def predict(self, X):
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X, num_iteration=self.model.best_iteration)
