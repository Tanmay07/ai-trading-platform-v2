"""
Application Configuration Module

Centralizes all configuration using Pydantic Settings.
Values are loaded from environment variables and/or a .env file.
This is for educational and research purposes only, not financial advice.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.

    All trading-related parameters are configurable here so that
    nothing is hardcoded in business logic.
    """

    # ── Application ───────────────────────────────────────────
    APP_NAME: str = "AI Trading Platform"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./trading.db"

    # ── API Keys ──────────────────────────────────────────────
    NEWS_API_KEY: str = ""
    GNEWS_API_KEY: str = ""

    # ── Default Watchlist (NSE symbols with .NS suffix) ──────
    DEFAULT_WATCHLIST: list[str] = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "LT.NS",
        "AXISBANK.NS",
        "BHARTIARTL.NS",
        "ITC.NS",
    ]

    # ── Market Indices ────────────────────────────────────────
    MARKET_INDEX: str = "^NSEI"      # NIFTY 50
    BANK_INDEX: str = "^NSEBANK"     # Bank Nifty

    # ── Trading Thresholds ────────────────────────────────────
    BUY_THRESHOLD: float = 0.3
    SELL_THRESHOLD: float = -0.3
    MAX_RISK_SCORE: float = 0.8

    # ── Cache ─────────────────────────────────────────────────
    CACHE_TTL_SECONDS: int = 300     # 5 minutes

    # ── yfinance Defaults ─────────────────────────────────────
    YFINANCE_HISTORY_PERIOD: str = "1y"

    # ── Technical Indicator Parameters ────────────────────────
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: int = 2

    # ── Moving Average Periods ────────────────────────────────
    SMA_PERIODS: list[int] = [5, 10, 20, 50, 100, 200]
    EMA_PERIODS: list[int] = [5, 10, 20, 50]

    # ── Confidence Thresholds (percentage) ────────────────────
    CONFIDENCE_HIGH: int = 70
    CONFIDENCE_MEDIUM: int = 50

    # ── Phase 2: Sentiment Analysis ──────────────────────────────
    SENTIMENT_WEIGHT: float = 0.10          # weight in combined score
    SENTIMENT_DECAY_HALF_LIFE_HOURS: int = 72   # 3-day decay
    SENTIMENT_MAX_ARTICLES: int = 20        # max articles per symbol
    SENTIMENT_CACHE_TTL_SECONDS: int = 900  # 15-min cache
    USE_FINBERT: bool = False               # opt-in for FinBERT
    NEWS_SOURCES: list[str] = ["newsapi", "gnews", "rss"]

    # ── Phase 3: ML Prediction Models ────────────────────────────
    ML_MODEL_DIR: str = "ml_models"          # directory for persisted models
    ML_PREDICTION_WEIGHT: float = 0.15       # weight in combined score
    ML_FORWARD_DAYS: int = 5                 # prediction horizon (trading days)
    ML_UP_THRESHOLD: float = 0.01            # return > +1% → UP
    ML_DOWN_THRESHOLD: float = -0.01         # return < -1% → DOWN
    ML_TEST_SIZE: float = 0.2                # train/test split ratio
    ML_MIN_TRAINING_ROWS: int = 200          # minimum clean rows to train
    ML_RETRAIN_DAYS: int = 30                # auto-retrain if model > 30 days old

    # ── Pydantic Settings Config ──────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",           # ignore unknown env vars
        case_sensitive=False,
    )


# Singleton instance used across the application
settings = Settings()
