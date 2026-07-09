# Phase E3: Institutional Dataset Engineering & ML Training Dataset Platform

## Overview
Phase E3 replaces the legacy ML Dataset Builder with a highly robust **Dataset Engineering Platform**. This platform is designed to eliminate common quantitative research pitfalls such as look-ahead bias, survivorship bias, and improper validation splits.

It acts as the strict middleman between the `Alpha Registry` and the actual `Model Training Platform`.

## Architecture & Workflow
1. **Feature Joiner**: Fetches OHLCV data and strictly joins it against only the highly ranked "Production/Experimental" features supplied by the Alpha Registry.
2. **Label Generator**: Dynamically generates multi-horizon targets without hardcoding thresholds. Supports `Breakout` (Binary) and `Classification` (Strong Buy/Sell) labels.
3. **Missing Value Handler**: Safely uses `forward_fill` or `median` strategies based on config to prepare the dataset for scikit-learn/XGBoost without leaking future data.
4. **Leakage Detector**: Specifically scans the output columns to ensure no feature contains `Target_`, `Future_`, or `Next_` data before finalizing the build.
5. **Quality Validator**: Evaluates class imbalances and overall missing row percentages, assigning a global Quality Score (0-100) to the dataset.
6. **Walk-forward Splitter**: Implements strict Time-Series Cross Validation. Random train/test splits are extremely dangerous in finance; this module ensures validation sets always strictly follow training sets chronologically.
7. **Dataset Registry**: Hashes the generated dataset and saves it to Parquet, while logging its metadata (rows, quality, feature count) into `dataset_registry.db`.

## Configuration (`config/dataset_platform.yaml`)
- Configures labeling thresholds (e.g., `Strong Buy` requires > 8% return).
- Configures missing value imputation strategies.
- Configures walk-forward windows (Train = 3 years, Val = 1 year, Test = 1 year).

## API & UI
- **APIs**: `/api/datasets/` to view the registry.
- **UI**: Added `Dataset Engineering` to the frontend sidebar to track generated dataset growth, quality metrics, and multi-class distribution.
