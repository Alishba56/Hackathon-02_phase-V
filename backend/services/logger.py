"""
Structured JSON Logger for Todo AI Chatbot Backend

This module provides structured logging with trace context, correlation IDs,
and JSON formatting for better observability in production environments.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variables for trace propagation
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.

    Includes:
    - Timestamp (ISO 8601)
    - Log level
    - Message
    - Trace context (trace_id, user_id, correlation_id)
    - Additional fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add trace context if available
        trace_id = trace_id_var.get()
        if trace_id:
            log_data["trace_id"] = trace_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }

        return json.dumps(log_data)


class StructuredLogger:
    """
    Structured logger wrapper with trace context support.

    Usage:
        logger = StructuredLogger(__name__)
        logger.info("Task created", task_id="task-123", user_id="user-456")
    """

    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)

        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal log method with extra fields."""
        extra_fields = {k: v for k, v in kwargs.items() if v is not None}
        self.logger.log(level, message, extra={'extra_fields': extra_fields})

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with extra fields."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with extra fields."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with extra fields."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with extra fields."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with extra fields."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        extra_fields = {k: v for k, v in kwargs.items() if v is not None}
        self.logger.exception(message, extra={'extra_fields': extra_fields})


def set_trace_context(trace_id: Optional[str] = None,
                     user_id: Optional[str] = None,
                     correlation_id: Optional[str] = None) -> None:
    """
    Set trace context for current request.

    Args:
        trace_id: W3C Trace Context trace ID
        user_id: User ID from authentication
        correlation_id: Correlation ID for request tracking
    """
    if trace_id:
        trace_id_var.set(trace_id)
    if user_id:
        user_id_var.set(user_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)


def clear_trace_context() -> None:
    """Clear trace context after request completion."""
    trace_id_var.set(None)
    user_id_var.set(None)
    correlation_id_var.set(None)


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context."""
    return trace_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return user_id_var.get()


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context."""
    return correlation_id_var.get()


# Create default logger instance
logger = StructuredLogger(__name__)
