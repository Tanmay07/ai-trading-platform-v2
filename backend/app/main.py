"""
FastAPI Application Entry Point

This is for educational and research purposes only, not financial advice.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import __version__
from app.config import settings
from app.database import init_db
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

    # Import models so Base.metadata is populated before create_all
    import app.models.portfolio  # noqa: F401
    import app.models.prediction  # noqa: F401
    import app.models.backtest  # noqa: F401
    import app.models.sentiment  # noqa: F401  (Phase 2)

    init_db()
    logger.info("✅ Application started successfully")

    yield  # ← application runs here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("🛑 Shutting down %s …", settings.APP_NAME)


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
    allow_origins=["*"],          # Allow all origins in dev mode
    allow_credentials=True,
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
from app.api.ml_routes import router as ml_router                # noqa: E402

app.include_router(market_router, prefix="/market", tags=["Market Data"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(prediction_router, prefix="/predictions", tags=["Predictions"])
app.include_router(sentiment_router, prefix="/sentiment", tags=["Sentiment"])
app.include_router(ml_router, prefix="/ml", tags=["ML"])


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
