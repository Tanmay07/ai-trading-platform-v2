"""
FastAPI Application Entry Point

This is for educational and research purposes only, not financial advice.
"""

import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import __version__
from app.config import settings
from app.discovery.scheduler import scheduled_discovery_scan
from app.suggestions.scheduler import scheduled_suggestion_scan
from app.utils.helpers import DISCLAIMER, get_ist_now
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # ── Startup ───────────────────────────────────────────────
    logger.info("🚀 Starting %s v%s", settings.APP_NAME, settings.VERSION)
    logger.info("📋 Debug mode: %s", settings.DEBUG)

    # Start the discovery scheduler background task (once every 24 hours)
    # discovery_task = asyncio.create_task(scheduled_discovery_scan(interval_minutes=1440))
    
    # Start the suggestion job background task (once every 2 hours)
    # suggestion_task = asyncio.create_task(scheduled_suggestion_scan(interval_minutes=120))

    logger.info("✅ Application started successfully")

    yield  # ← application runs here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("🛑 Shutting down %s …", settings.APP_NAME)
    # discovery_task.cancel()
    # suggestion_task.cancel()
    try:
        # await discovery_task
        # await suggestion_task
        pass
    except asyncio.CancelledError:
        logger.info("✅ Discovery and Suggestion schedulers stopped")


# ── FastAPI Application ──────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "An AI-powered advisory platform for the Indian stock market (NSE). "
        "Provides technical analysis, portfolio management, and ML-based "
        "predictions in paper-trading / advisory mode.\n\n"
        f"**⚠️ Disclaimer:** {DISCLAIMER}"
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── Middleware ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API Routers ──────────────────────────────────────
# Lazy-import routers to avoid circular-import issues and allow
# each module to import from database/config freely.
from app.api.market_routes import router as market_router       # noqa: E402
from app.api.portfolio_routes import router as portfolio_router  # noqa: E402
from app.api.prediction_routes import router as prediction_router  # noqa: E402
from app.api.sentiment_routes import router as sentiment_router  # noqa: E402
from app.api.discovery_routes import router as discovery_router  # noqa: E402
from app.api.ml_routes import router as ml_router                # noqa: E402
from app.api.ml_models_routes import router as ml_models_router  # noqa: E402
from app.api.reinforcement_routes import router as reinforcement_router # noqa: E402
from app.api.backtest_routes import router as backtest_router    # noqa: E402
from app.api.ws_routes import router as ws_router                # noqa: E402
from app.api.suggestion_routes import router as suggestion_router # noqa: E402
from app.api.paper_trading_routes import router as paper_trading_router # noqa: E402
from app.api.trade_outcomes_routes import router as trade_outcomes_router
from app.api.validation_routes import router as validation_router
from app.api.model_routes import router as model_router
app.include_router(model_router, prefix="/api/model", tags=["Model Intelligence"])
app.include_router(paper_trading_router, prefix="/paper-trading", tags=["Paper Trading"])
app.include_router(prediction_router, prefix="/predictions", tags=["Predictions"])
app.include_router(sentiment_router, prefix="/sentiment", tags=["Sentiment"])
app.include_router(market_router, prefix="/market", tags=["Market Data"])
app.include_router(suggestion_router, prefix="/suggestions", tags=["Suggestions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])

from app.api.execution_routes import router as execution_router
app.include_router(execution_router, prefix="/execution", tags=["Execution"])

from app.api.committee_routes import router as committee_router
app.include_router(committee_router, prefix="/committee", tags=["Committee"])

from app.api.paper_trading_routes import router as paper_trading_router
app.include_router(paper_trading_router, prefix="/paper_trading", tags=["Paper Trading"])

from app.api.adaptive_routes import router as adaptive_router
app.include_router(adaptive_router, prefix="/adaptive", tags=["Adaptive Learning"])

from app.api.operations_routes import router as operations_router
app.include_router(operations_router, prefix="/operations", tags=["Trading Operations"])

from app.api.strategy_routes import router as strategy_router
app.include_router(strategy_router, prefix="/strategies", tags=["Multi-Strategy"])

from app.api.optimizer_routes import router as optimizer_router
app.include_router(optimizer_router, prefix="/optimizer", tags=["Portfolio Optimizer"])
app.include_router(validation_router, prefix="/api/validation", tags=["Validation Engine"])
from app.api.backtesting_v2_routes import router as backtesting_v2_router

from app.api.trading_routes import router as trading_router

from app.api.admin_routes import router as admin_router

from app.api.research_routes import router as research_router
from app.api.factor_routes import router as factor_router
from app.api.benchmark_routes import router as benchmark_router
from app.api.production_routes import router as production_router

from app.api.hfos_routes import router as hfos_router

from app.api.data_platform_routes import router as data_platform_router

from app.api.scenario_routes import router as scenario_router
from app.api.recommendation_routes import router as recommendation_router
from app.api.training_routes import router as training_framework_router

from app.api.trade_outcomes_routes import router as trade_outcomes_router

app.include_router(discovery_router, prefix="/discovery", tags=["Discovery"])
app.include_router(ml_router, prefix="/ml", tags=["ML"])
app.include_router(ml_models_router, tags=["ML Models"])
app.include_router(reinforcement_router, tags=["Reinforcement Learning"])
app.include_router(backtest_router, prefix="/backtest", tags=["Backtest"])
app.include_router(backtesting_v2_router, tags=["Backtesting V2"])
app.include_router(trading_router, tags=["Live Trading Phase 5"])
app.include_router(admin_router, tags=["Admin Enterprise"])
app.include_router(research_router, tags=["Autonomous Research"])
app.include_router(factor_router, tags=["Factor Engine"])
app.include_router(benchmark_router, tags=["Model Arena"])
app.include_router(production_router, tags=["Production Model"])
app.include_router(hfos_router, tags=["Hedge Fund OS"])
app.include_router(data_platform_router, tags=["Data Platform"])
app.include_router(trade_outcomes_router, prefix="/api/trade-outcomes", tags=["trade-outcomes"])

from app.api.ml_platform_routes import router as ml_platform_router
app.include_router(ml_platform_router)

from app.api.market_data_routes import router as market_data_router
app.include_router(market_data_router)

from app.api.market_intelligence_routes import router as market_intelligence_router
app.include_router(market_intelligence_router)

from app.api.decision_routes import router as decision_router
app.include_router(decision_router)

from app.api.prediction_feedback_routes import router as prediction_feedback_router
app.include_router(prediction_feedback_router)

from app.api.bootstrap_routes import router as bootstrap_router
app.include_router(bootstrap_router)

from app.api.tradability_routes import router as tradability_router
app.include_router(tradability_router)

from app.api.feature_routes import router as feature_router
app.include_router(feature_router, prefix="/api/features", tags=["Feature Intelligence"])

from app.api.alpha_routes import router as alpha_router
app.include_router(alpha_router)

from app.api.dataset_routes import router as dataset_router
app.include_router(dataset_router)

from app.api.research_routes import router as research_router
app.include_router(research_router, prefix="/research", tags=["Alpha Research"])

from app.api.scenario_routes import router as scenario_router
app.include_router(scenario_router)

app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
from app.api.recommendation_routes import router as recommendation_router
app.include_router(recommendation_router, tags=["Recommendations"])
app.include_router(training_framework_router)


# ── Root Endpoints ────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns the application status, version, current IST timestamp,
    and the mandatory disclaimer.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "timestamp": get_ist_now().isoformat(),
        "debug": settings.DEBUG,
        "disclaimer": DISCLAIMER,
    }
