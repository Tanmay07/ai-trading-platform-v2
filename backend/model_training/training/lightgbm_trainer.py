import lightgbm as lgb
import logging

logger = logging.getLogger("LightGBMTrainer")

class LightGBMTrainer:
    def __init__(self, params: dict = None):
        self.default_params = {
            'objective': 'binary',
            'metric': ['auc', 'binary_logloss'],
            'learning_rate': 0.03,
            'num_leaves': 64,
            'max_depth': 8,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'n_estimators': 500,
            'verbose': -1,
            'early_stopping_rounds': 50
        }
        
        if params:
            self.params = {**self.default_params, **params}
        else:
            self.params = self.default_params
            
        self.model = None

    def train(self, X_train, y_train, X_val, y_val):
        """
        Trains the LightGBM model with early stopping on the validation set.
        """
        logger.info("Starting LightGBM training...")
        
        # Pop n_estimators and early_stopping_rounds for train() signature if needed,
        # but the scikit-learn API LGBMClassifier handles them well.
        # We will use the standard native lightgbm API for better control.
        
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # Extract training specific kwargs
        num_boost_round = self.params.pop('n_estimators', 500)
        early_stopping = self.params.pop('early_stopping_rounds', 50)
        
        callbacks = [
            lgb.early_stopping(stopping_rounds=early_stopping, verbose=True),
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
        
        logger.info(f"Training complete. Best iteration: {self.model.best_iteration}")
        return self.model

    def predict_proba(self, X):
        """Returns the raw probability of the positive class."""
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X, num_iteration=self.model.best_iteration)
