"""Structured logging configuration for GuitarScapes Pro.

Provides console and optional file logging with rotation support.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


_LOGGER_NAME = "guitarscapes"

_LOG_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(name)-20s] %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    """Configure the application-wide logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path for file logging with rotation.
        max_bytes: Maximum log file size before rotation.
        backup_count: Number of rotated log files to keep.

    Returns:
        The configured root logger for the application.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Prevent duplicate handlers on re-initialization
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (optional)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the application namespace.

    Args:
        name: Module or component name (e.g., 'audio.capture').

    Returns:
        A logger instance scoped to the application.
    """
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")
