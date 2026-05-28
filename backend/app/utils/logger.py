"""
Logging Utility

Provides a pre-configured logger factory that writes to both the console
(with optional colour) and a rotating log file.
"""

import logging
import os
import sys
from pathlib import Path


# ── ANSI colour codes for console output ──────────────────────
_COLOURS = {
    "DEBUG": "\033[36m",      # cyan
    "INFO": "\033[32m",       # green
    "WARNING": "\033[33m",    # yellow
    "ERROR": "\033[31m",      # red
    "CRITICAL": "\033[1;31m", # bold red
    "RESET": "\033[0m",
}


class _ColouredFormatter(logging.Formatter):
    """Formatter that injects ANSI colour codes around the log level."""

    def __init__(self, fmt: str, datefmt: str | None = None) -> None:
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        colour = _COLOURS.get(record.levelname, "")
        reset = _COLOURS["RESET"]
        record.levelname = f"{colour}{record.levelname:<8}{reset}"
        return super().format(record)


# ── Log directory bootstrap ───────────────────────────────────
_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "trading.log"

# ── Shared format strings ────────────────────────────────────
_LOG_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# Detect debug mode from environment (avoids circular import of config)
_DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured :class:`logging.Logger` for the given *name*.

    * **Console handler** — coloured output to *stderr*.
    * **File handler** — plain-text output to ``logs/trading.log``.
    * Log level is ``DEBUG`` when the ``DEBUG`` env var is truthy,
      otherwise ``INFO``.

    Parameters
    ----------
    name:
        Typically ``__name__`` of the calling module.

    Returns
    -------
    logging.Logger
        Ready-to-use logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when get_logger is called
    # multiple times with the same name (e.g. module reloads).
    if logger.handlers:
        return logger

    level = logging.DEBUG if _DEBUG else logging.INFO
    logger.setLevel(level)

    # ── Console handler ───────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(_ColouredFormatter(_LOG_FMT, _LOG_DATE_FMT))
    logger.addHandler(console_handler)

    # ── File handler ──────────────────────────────────────────
    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # always capture everything in file
    file_handler.setFormatter(logging.Formatter(_LOG_FMT, _LOG_DATE_FMT))
    logger.addHandler(file_handler)

    # Prevent log propagation to the root logger
    logger.propagate = False

    return logger
