# Frontend Phase F2: Data Intelligence Platform

## Overview
Phase F2 extends the React frontend to visualize and monitor the enterprise-grade AI infrastructure built in backend Phases D1–D6. Rather than just seeing predictions, the user now has full visibility into the AI's "brain" and the data pipelines feeding it.

## New UI Sections (AI Platform)

### 1. Data Intelligence (`/platform/data`)
- Monitors Phase D1 (Historical Data Lake) and D3 (Smart Market Data).
- Displays Universe coverage (e.g., 2,348 stocks), storage size (Parquet format), and download status.
- Shows storage health across SQLite, AWS S3, and Metadata DB.

### 2. Model Intelligence (`/platform/model`)
- Visualizes Phase D2 (Feature Store & Model Training).
- Displays the active models in the registry (e.g., Meta Ensemble, XGBoost, LightGBM).
- Tracks Feature Importance (Top 30 features) and Model accuracy, precision, and recall metrics.

### 3. Prediction Intelligence (`/platform/prediction`)
- Visualizes Phase D5 and D6 (Prediction Tracking & Meta Decision).
- Shows aggregate stats like Win Rate (71%), Target Hits (63%), and Average Return.
- Displays a lifecycle table of Active, Winning, and Losing predictions.
- Shows Confidence Calibration metrics.

### 4. Market Intelligence Hub (`/platform/market-hub`)
- Upgrades the existing Market Intelligence view to support Phase D4.
- Adds tabs for News Sentiment, Corporate Actions, and Sector Rotation.
- Displays processed NLP news feeds with Sentiment and Impact scores, alongside trending companies.

### 5. Platform Health (`/platform/health`)
- A Mission Control dashboard for system monitoring.
- Tracks the health of Core Infrastructure (D1-D6), Databases (Redis, Postgres, SQLite), and API Consumption (Yahoo, NSE, Cache Hit Rates).

### 6. Continuous Learning (`/platform/learning`)
- Visualizes Phase D6's feedback loop.
- Tracks Retraining Queues, Feature Drift, and Recent Analyzed Learnings (Success/Failure factors).
- Shows Model Evolution (v7 -> v8 -> v8.4) improvements.

## Enhancements
- **Dashboard**: Added an "AI Platform Health Snapshot" row at the top to give a quick glance at the underlying systems.
- **Research Lab**: Added new tabs (Datasets, Feature Store, Training Runs, Prediction Feedback).
- **Command Center**: Updated system metrics to track Phase D2-D6 statuses.

## Tech Stack & Architecture
- **React 19+**: Pure functional components with hooks.
- **TailwindCSS**: Used for rapid, beautiful, dark-mode first styling.
- **Lucide React**: Vector icons used consistently across new components.
- **Routing**: `react-router-dom` v6 updated in `App.jsx`. No existing routes were removed or modified.
