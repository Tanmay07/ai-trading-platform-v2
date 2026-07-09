# Phase D4: Market Intelligence Platform

## Overview
The Market Intelligence Platform turns unstructured news and corporate announcements into highly structured, actionable AI features. It operates entirely independently, feeding clean signals downstream to the AI Supervisor, Portfolio Optimizer, and the D2 Feature Store.

## Architecture Pipeline
The ingestion and processing pipeline follows a strict, sequential order defined in `app/api/market_intelligence_routes.py`:

1. **News Collector & RSS Providers**: Fetches articles from Google News, Moneycontrol, etc., using `feedparser`.
2. **Deduplicator**: Hashes `title + source + time` with SHA256 to ensure zero duplicate inferences.
3. **Article Parser**: Cleans HTML from the feed summary text.
4. **Company Tagger**: Matches text to known NSE symbols (e.g. `["reliance", "ril"]` -> `RELIANCE`).
5. **Event Classifier**: Categorizes the news (Earnings, Business, Macro, Risk) using keyword heuristics.
6. **Sentiment Engine (FinBERT)**: Uses `Transformers` to load `ProsusAI/finbert`. It processes text natively via `torch` (using MPS on Mac if available, otherwise CPU). Outputs probability scores for Positive, Negative, and Neutral.
7. **News Importance Scorer**: Calculates a normalized 0-100 score based on source authority, event weight, and sentiment confidence.
8. **Market Memory Engine (Institutional Edge)**: Matches the event to historical data to output validated statistics (e.g. "This type of event leads to 8.6% returns with 78% win rate").
9. **Feature Store Push**: Routes numerical metrics (sentiment score, importance) back to `ml_platform/feature_store/`.

## Data Models
The data is persisted via SQLAlchemy in the `articles` and `market_memory_events` tables defined in `storage/models.py`. 
Each `Article` entity contains the NLP outputs:
- `sentiment_label`
- `sentiment_score`
- `importance_score`
- `company_tags`
- `event_classification`

## Configuration
Controlled entirely via `config/market_intelligence.yaml`. 
Adjust `scoring_weights`, `schedule` intervals, and configure the `ProsusAI/finbert` model.

## API Endpoints
- `GET /api/news/latest`: Fetches recently processed articles.
- `POST /api/news/process`: Triggers a background task that runs the entire Pipeline described above.
