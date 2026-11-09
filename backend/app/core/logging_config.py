"""
Logging configuration for Product Hunter AI.
Provides structured JSON logging for agents and system events.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class LogContext(BaseModel):
    """Structured context for log entries."""
    agent: str | None = None
    product_id: str | None = None
    source: str | None = None
    duration_ms: int | None = None
    retry_count: int | None = None
    error_type: str | None = None


class StructuredLogFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add stack info if present
        if record.stack_info:
            log_entry["stack"] = self.formatStack(record.stack_info)

        # Add extra context if provided
        if hasattr(record, 'context'):
            context = record.context.model_dump(exclude_none=True)
            log_entry["context"] = context

        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging for the application.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with structured output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(StructuredLogFormatter())

    root_logger.addHandler(console_handler)

    # Set default log levels for third-party libraries
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str, context: dict | None = None) -> logging.Logger:
    """
    Get a logger with optional context.

    Usage:
        logger = get_logger(__name__, {"agent": "discovery"})
        logger.info("Starting discovery", extra={"context": context_dict})
    """
    logger = logging.getLogger(name)

    if context:
        logger.context = LogContext(**context)
    else:
        logger.context = LogContext()

    return logger