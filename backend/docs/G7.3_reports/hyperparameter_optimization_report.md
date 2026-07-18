# Hyperparameter Optimization Report

## LightGBM
**Best ROC_AUC:** 0.5455
**Best Params:** `{"num_leaves": 128, "learning_rate": 0.1, "max_depth": 6, "feature_fraction": 1.0, "bagging_fraction": 1.0, "bagging_freq": 0, "min_child_samples": 50, "lambda_l1": 0.0, "lambda_l2": 0.0, "min_split_gain": 0.01}`

## XGBoost
**Best ROC_AUC:** 0.5465
**Best Params:** `{"max_depth": 4, "learning_rate": 0.1, "min_child_weight": 1, "gamma": 0.2, "subsample": 0.8, "colsample_bytree": 1.0, "reg_alpha": 0.1, "reg_lambda": 0.1, "n_estimators": 200}`

## CatBoost
**Best ROC_AUC:** 0.5386
**Best Params:** `{"depth": 4, "learning_rate": 0.01, "iterations": 500, "l2_leaf_reg": 5, "bagging_temperature": 1.0, "random_strength": 10, "border_count": 64}`

