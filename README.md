# 🇮🇳 AI Trading Platform — Indian Stock Market

An AI-powered trading advisory platform for the Indian stock market (NSE).  
Provides technical analysis, portfolio management, and ML-based predictions — all in **paper-trading / advisory mode**.

> ⚠️ **DISCLAIMER**: This is for **educational and research purposes only**, not financial advice.  
> The creators are not responsible for any financial decisions made using this platform.  
> Always consult a certified financial advisor before making investment decisions.

---

## 📦 Tech Stack

| Layer          | Technology                                      |
|----------------|--------------------------------------------------|
| **Backend**    | Python 3.11+, FastAPI, Uvicorn                   |
| **Database**   | SQLite (via SQLAlchemy ORM)                       |
| **Market Data**| yfinance (Yahoo Finance API)                      |
| **Analysis**   | pandas, NumPy, Technical Indicators               |
| **NLP (Phase 2)** | VADER Sentiment, FinBERT (opt-in)             |
| **ML (Phase 3)**  | scikit-learn, XGBoost, LightGBM                |

---

## 🚀 Quick Start (macOS)

### Prerequisites

```bash
# Install system dependencies (needed for LightGBM/XGBoost in later phases)
brew install libomp cmake
```

### Setup

```bash
# 1. Clone the repository
git clone <repo-url> ai-trading-platform
cd ai-trading-platform

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys (optional for Phase 1)

# 5. Start the development server
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**  
Interactive docs at **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

### General
| Method | Endpoint     | Description              |
|--------|-------------|--------------------------|
| GET    | `/`          | Redirect to API docs     |
| GET    | `/health`    | Health check + version   |

### Market Data (`/api/v1/market`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/quote/{symbol}`         | Get current price & quote          |
| GET    | `/ohlcv/{symbol}`         | Get OHLCV historical data          |
| GET    | `/watchlist`              | Get watchlist with live prices     |
| GET    | `/info/{symbol}`          | Get detailed stock info            |

### Portfolio (`/api/v1/portfolio`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/holdings`               | List all portfolio holdings        |
| POST   | `/holdings`               | Add a new holding                  |
| GET    | `/summary`                | Portfolio summary with P&L         |
| GET    | `/transactions`           | Transaction history                |

### Predictions (`/api/v1/predictions`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/analyze/{symbol}`       | Get AI analysis & recommendation   |
| GET    | `/signals/{symbol}`       | Get technical signals              |
| GET    | `/history`                | Past predictions & outcomes        |

### Sentiment (`/api/v1/sentiment`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/{symbol}`               | Aggregated sentiment for a stock   |
| GET    | `/{symbol}/articles`      | Recent news with sentiment scores  |
| GET    | `/market/overview`        | Market-wide sentiment overview     |

### ML (`/api/v1/ml`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/train/{symbol}`         | Train ML models for a stock        |
| POST   | `/train-all`              | Batch train for entire watchlist   |
| GET    | `/predict/{symbol}`       | Get ML prediction (UP/DOWN/NEUTRAL)|
| GET    | `/status/{symbol}`        | Model training status & metrics    |
| GET    | `/status`                 | Status for all trained models      |

### Backtesting (`/api/v1/backtest`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/run`                    | Run backtest (symbol, date range)  |
| GET    | `/runs`                   | List history of backtest runs      |
| GET    | `/runs/{run_id}`          | Detailed metrics and trade history |

---

## 🗂️ Project Structure

```
ai-trading-platform/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application entry point
│       ├── config.py            # Pydantic Settings configuration
│       ├── database.py          # SQLAlchemy engine & session
│       ├── models/              # ORM models (portfolio, predictions, backtest, sentiment)
│       ├── api/                 # FastAPI route handlers
│       │   ├── market_routes.py
│       │   ├── portfolio_routes.py
│       │   ├── prediction_routes.py
│       │   ├── sentiment_routes.py     # Phase 2: Sentiment API
│       │   ├── ml_routes.py            # Phase 3: ML API
│       │   └── backtest_routes.py      # Phase 4: Backtest API
│       ├── backtest/            # Backtesting Engine
│       │   ├── __init__.py
│       │   └── engine.py               # Phase 4: Event-driven simulator
│       ├── data/                # Market data & news services
│       │   ├── market_data_service.py
│       │   ├── live_data_service.py
│       │   ├── historical_data_service.py
│       │   └── news_service.py         # Phase 2: Multi-source news
│       ├── features/            # Feature engineering pipeline
│       │   ├── technical_features.py
│       │   ├── volume_features.py
│       │   ├── volatility_features.py
│       │   ├── feature_pipeline.py
│       │   ├── sentiment_analyzer.py   # Phase 2: VADER/FinBERT NLP
│       │   └── sentiment_features.py   # Phase 2: Sentiment features
│       ├── ml/                  # Machine learning pipeline
│       │   ├── ml_data_preparer.py     # Phase 3: Feature + label prep
│       │   ├── models.py               # Phase 3: XGBoost/LightGBM/Ensemble
│       │   └── model_manager.py        # Phase 3: Train/predict orchestrator
│       ├── strategies/          # Trading strategy logic
│       │   ├── rule_based_strategy.py
│       │   └── recommendation_engine.py
│       ├── portfolio/           # Portfolio management
│       │   ├── portfolio_service.py
│       │   └── risk_analyzer.py
│       └── utils/               # Shared utilities
│           ├── logger.py
│           └── helpers.py
└── frontend/                    # (Future: React/Next.js dashboard)
```

---

## 🛣️ Roadmap

- [x] **Phase 1**: Core infrastructure, market data, technical analysis, portfolio management
- [x] **Phase 2**: News sentiment analysis (NLP), multi-source news aggregation
- [x] **Phase 3**: ML prediction models (XGBoost, LightGBM, ensemble)
- [x] **Phase 4**: Backtesting engine, strategy optimization
- [x] **Phase 5**: Frontend dashboard, real-time WebSocket updates

---

## 📜 License

This project is for educational and research purposes only.
