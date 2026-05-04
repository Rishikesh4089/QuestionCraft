# app/core/logging.py
"""
Structured logging configuration.
- Development: human-readable colourised output
- Production (LOG_JSON=true): JSON lines for log aggregators (Datadog, Loki, etc.)
"""
from __future__ import annotations

import logging
import sys

try:
    from pythonjsonlogger import jsonlogger  # type: ignore
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False


_COLOURS = {
    "DEBUG":    "\033[36m",   # cyan
    "INFO":     "\033[32m",   # green
    "WARNING":  "\033[33m",   # yellow
    "ERROR":    "\033[31m",   # red
    "CRITICAL": "\033[35m",   # magenta
    "RESET":    "\033[0m",
}


class ColourFormatter(logging.Formatter):
    """Human-readable colourised formatter for dev environments."""

    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelname, "")
        reset  = _COLOURS["RESET"]
        # Use %-style so logging fills in %(asctime)s etc. before we see it
        fmt = f"{colour}[%(levelname)-8s]{reset} %(asctime)s | %(name)s | %(message)s"
        formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """
    Call once at application startup (in main.py lifespan).
    Subsequent calls are idempotent.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()

    if root.handlers:
        root.setLevel(numeric_level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if json_logs and HAS_JSON_LOGGER:
        formatter = jsonlogger.JsonFormatter(  # type: ignore[attr-defined]
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = ColourFormatter()

    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(numeric_level)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "openai._base_client", "faiss"):
        logging.getLogger(noisy).setLevel(logging.WARNING)