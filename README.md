# 🇮🇳 AI Trading Platform — Indian Stock Market

An AI-powered trading advisory platform for the Indian stock market (NSE).  
Provides technical analysis, portfolio management, ML-based predictions, and a continuous **AI Opportunity Discovery Engine** — all in **paper-trading / advisory mode**.

> ⚠️ **DISCLAIMER**: This is for **educational and research purposes only**, not financial advice.  
> The creators are not responsible for any financial decisions made using this platform.  
> Always consult a certified financial advisor before making investment decisions.

---

## 📦 Tech Stack

| Layer          | Technology                                      |
|----------------|--------------------------------------------------|
| **Backend**    | Python 3.11+, FastAPI, Uvicorn                   |
| **Database**   | S3 Storage Service, SQLite (via SQLAlchemy ORM)  |
| **Frontend**   | React (Vite), Lucide Icons                       |
| **Market Data**| yfinance (Yahoo Finance API)                      |
| **Analysis**   | pandas, NumPy, `ta` (Technical Analysis)          |
| **NLP**        | VADER Sentiment, FinBERT (HuggingFace)            |
| **ML**         | scikit-learn, XGBoost, LightGBM (Ensembles)      |

---

## 🚀 Key Features

### 1. Portfolio Tracking
Live P&L tracking, 1y/5d historical charting, sector exposure analysis, and automated market price syncing via Yahoo Finance.

### 2. Market Sentiment Analysis
Pulls live news articles from GNews and RSS feeds and runs them through a localized instance of **FinBERT** to score the market sentiment for individual stocks as Bearish, Neutral, or Bullish.

### 3. AI Opportunity Discovery Engine
A comprehensive background scanning engine that continually analyzes the NSE universe. It generates an **Opportunity Score (0-100)** by combining:
- **Fundamental Engine:** Scores based on ROE, Margins, Debt/Equity, and Growth.
- **Value Engine:** Identifies fundamentally strong stocks trading near their 52-week lows.
- **Momentum Engine:** Vectorized calculation of RSI, MACD crossovers, and Bollinger Bands.
- **Sentiment Engine:** Real-time news NLP processing.
- **AI Predictor:** Generates probability metrics for a 5%+ return over the next 30 days.
- **Sector Strength:** Tracks relative momentum across sectors.

### 4. Enterprise Data & AI Pipelines
- **Historical Data Lake (Phase D1):** High-performance storage and retrieval of OHLCV data using Parquet files and Redis caching.
- **Feature Store Platform (Phase D2):** A centralized, versioned repository of engineered Alpha Factors optimized for quantitative modeling.
- **Alpha Registry (Phase E2.1):** A research platform that tracks Information Coefficient (IC) and stability of engineered Alpha Factors over time.
- **Hierarchical Scenario Datasets (Phase E3.1):** Dynamically segments the NSE universe into specialized subsets (Bull Market, Sectors, High Volatility) to train expert models instead of one generic model.
- **Intelligent Bootstrap Manager (Phase E1.5):** A resumable orchestration layer that tracks initialization stages across the platform, including a Preflight Estimation Engine.

---

## 🚀 Quick Start (macOS)

### Prerequisites

```bash
# Install system dependencies (needed for LightGBM/XGBoost)
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
# Edit .env with your API keys (GNEWS_API_KEY, etc.)

# 5. Start the backend server
uvicorn app.main:app --reload --port 8000

# 6. Start the frontend server (in a new terminal)
cd ../frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:5173**  
The API will be available at **http://127.0.0.1:8000**  
Interactive docs at **http://127.0.0.1:8000/docs**

---

## 📡 Key API Endpoints

### Discovery (`/discovery`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/scan`                   | Get the latest AI Discovery Scan   |
| GET    | `/top/{category}`         | Filter top opportunities by category (e.g. `high_growth`, `value`, `momentum`) |

### AI Platform & Orchestration
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/api/bootstrap/preflight`| Run Bootstrap Preflight checks     |
| GET    | `/api/scenarios/`         | View Scenario Generation metrics   |
| GET    | `/api/datasets/`          | View ML Dataset Builder metrics    |
| GET    | `/api/alpha/`             | Access the Alpha Research Registry |

### Portfolio (`/portfolio`)
| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/`                       | List all portfolio holdings        |
| POST   | `/`                       | Add a new holding                  |
| DELETE | `/{symbol}`               | Remove a holding                   |

---

## 🗓️ Roadmap

- [x] Phase 1-4: Core Market Data & Sentiment Discovery
- [x] Phase D1-D2: Historical Data Lake & Feature Store
- [x] Phase E2-E3: Alpha Registry & Scenario Datasets
- [x] Phase E1.5: Production Bootstrap Manager
- [ ] Phase 5: Live Trading API integrations (Broker APIs)
