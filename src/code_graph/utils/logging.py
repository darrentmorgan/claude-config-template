"""Structured logging with correlation IDs for code graph indexer.

Provides consistent logging across the application with trace correlation.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Optional


# Context variable for correlation ID (thread-safe)
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationFormatter(logging.Formatter):
    """Custom formatter that includes correlation ID."""

    def format(self, record: logging.LogRecord) -> str:
        """Add correlation ID to log record."""
        correlation_id = _correlation_id.get()
        record.correlation_id = correlation_id or "no-correlation"  # type: ignore
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_format: Whether to use JSON format (for production)
    """
    log_level = getattr(logging, level.upper())

    # Create formatter
    if json_format:
        # Structured JSON format for production
        fmt = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "correlation_id": "%(correlation_id)s", "logger": "%(name)s", "message": "%(message)s"}'
    else:
        # Human-readable format for development
        fmt = "%(asctime)s [%(correlation_id)s] %(levelname)-8s %(name)s - %(message)s"

    formatter = CorrelationFormatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("gqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for current context.

    Args:
        correlation_id: Correlation ID to use. If None, generates new UUID.

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _correlation_id.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID.

    Returns:
        Current correlation ID or None
    """
    return _correlation_id.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from current context."""
    _correlation_id.set(None)
