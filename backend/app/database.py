"""
Database Module

Sets up SQLAlchemy engine, session factory, and declarative base.
Provides a FastAPI-compatible dependency for database sessions.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


# ── Engine ────────────────────────────────────────────────────
# SQLite needs check_same_thread=False when used with FastAPI's
# threaded request handling.
_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=settings.DEBUG,          # log SQL statements in debug mode
    pool_pre_ping=True,           # verify connections before use
)


def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode and foreign keys for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Attach the pragma listener only for SQLite databases
if settings.DATABASE_URL.startswith("sqlite"):
    event.listen(engine, "connect", _set_sqlite_pragma)


# ── Session Factory ───────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── FastAPI Dependency ────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for FastAPI route handlers.

    Usage::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...

    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Initialization ────────────────────────────────────────────
def init_db() -> None:
    """
    Create all database tables that don't yet exist.

    Called once during application startup. Models must be imported
    before this function is called so that ``Base.metadata`` is
    fully populated.
    """
    logger.info("Initializing database tables …")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete.")
